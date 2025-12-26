"""Interactive console viewer for Klipper output."""

import threading
import time
from collections import deque
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from .handlers import Handlers


class ConsoleViewer:
    """Interactive console viewer with real-time updates."""

    def __init__(self, handlers: "Handlers", max_messages: int = 1000, split_screen: bool = False):
        """
        Initialize console viewer.

        Args:
            handlers: Handlers instance for executing commands
            max_messages: Maximum messages to keep in buffer
            split_screen: Enable split-screen mode with status panel
        """
        self.handlers = handlers
        self.messages = deque(maxlen=max_messages)
        self.console = Console()
        self.running = False
        self.ws_client = None
        self.display_lock = threading.Lock()
        self.last_display_time = 0
        self.display_interval = 0.1  # Limit updates to 10 per second

        # Command history for up/down arrow navigation
        self.history = InMemoryHistory()

        # Split-screen mode configuration
        self.split_screen = split_screen
        self.status_data: dict = {}
        self.status_thread: Optional[threading.Thread] = None
        self.status_running = False
        self.status_update_interval = 2.0  # seconds

        # Get available G-code commands for completion
        try:
            gcode_commands = handlers.list_gcode_commands()
            self.completer = WordCompleter(gcode_commands, ignore_case=True)
        except Exception:
            # Fallback if we can't get commands
            self.completer = None

    def add_message(self, message: str, timestamp: float = None, msg_type: str = "response"):
        """Add a message to the buffer."""
        if timestamp is None:
            timestamp = time.time()

        dt = datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%H:%M:%S")

        with self.display_lock:
            self.messages.append({
                "time": time_str,
                "message": message,
                "type": msg_type
            })

    def format_messages(self) -> Text:
        """Format messages for display."""
        text = Text()

        with self.display_lock:
            for msg in self.messages:
                # Color code by type
                if msg["type"] == "command":
                    color = "cyan"
                elif msg["type"] == "error":
                    color = "red"
                elif msg["type"] == "warning":
                    color = "yellow"
                else:
                    color = "white"

                text.append(f"[{msg['time']}] ", style="dim")
                text.append(f"{msg['message']}\n", style=color)

        return text

    def _query_status_data(self) -> dict:
        """Query current printer status for split-screen display."""
        status = {}

        try:
            status['printer_state'] = self.handlers.get_printer_status()
        except Exception:
            status['printer_state'] = None

        try:
            status['print_status'] = self.handlers.get_print_status()
        except Exception:
            status['print_status'] = None

        try:
            heaters = self.handlers.get_all_heaters()
            status['extruder'] = next((h for h in heaters if h.name == 'extruder'), None)
            status['bed'] = next((h for h in heaters if 'bed' in h.name.lower()), None)
        except Exception:
            status['extruder'] = None
            status['bed'] = None

        try:
            status['toolhead'] = self.handlers.get_toolhead()
        except Exception:
            status['toolhead'] = None

        try:
            fans = self.handlers.get_all_fans()
            status['fan'] = next((f for f in fans if f.name == 'fan'), None)
        except Exception:
            status['fan'] = None

        return status

    def format_status_panel(self) -> Table:
        """Format status information as a compact table."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="right")
        table.add_column()

        with self.display_lock:
            status = self.status_data

        # Printer state with color coding
        if status.get('printer_state'):
            state = status['printer_state'].state
            if state == 'ready':
                state_text = f"[green]{state.upper()}[/green]"
            elif state in ['error', 'shutdown']:
                state_text = f"[red]{state.upper()}[/red]"
            elif state == 'printing':
                state_text = f"[yellow]{state.upper()}[/yellow]"
            else:
                state_text = f"[cyan]{state.upper()}[/cyan]"
            table.add_row("State:", state_text)

        # Extruder temperature
        if status.get('extruder'):
            ext = status['extruder']
            temp_color = "yellow" if ext.target > 0 and ext.temperature < ext.target - 5 else "green"
            target_str = f"/{ext.target:.0f}" if ext.target > 0 else ""
            table.add_row(
                "Extruder:",
                f"[{temp_color}]{ext.temperature:.1f}{target_str}°C[/{temp_color}] ({ext.power*100:.0f}%)"
            )

        # Bed temperature
        if status.get('bed'):
            bed = status['bed']
            temp_color = "yellow" if bed.target > 0 and bed.temperature < bed.target - 5 else "green"
            target_str = f"/{bed.target:.0f}" if bed.target > 0 else ""
            table.add_row(
                "Bed:",
                f"[{temp_color}]{bed.temperature:.1f}{target_str}°C[/{temp_color}] ({bed.power*100:.0f}%)"
            )

        # Print progress (if actively printing)
        if status.get('print_status'):
            ps = status['print_status']
            if ps.state == 'printing' and ps.progress > 0:
                table.add_row("File:", ps.filename)
                table.add_row("Progress:", f"{ps.progress*100:.1f}%")

                # Time remaining
                if ps.progress > 0 and ps.progress < 1.0:
                    remaining = (ps.print_duration / ps.progress) - ps.print_duration
                    hours = int(remaining // 3600)
                    minutes = int((remaining % 3600) // 60)
                    table.add_row("Remaining:", f"~{hours:02d}:{minutes:02d}")

        # Toolhead position
        if status.get('toolhead'):
            th = status['toolhead']
            homed = f"[green]Homed: {th.homed_axes.upper()}[/green]" if th.homed_axes else "[red]Not homed[/red]"
            table.add_row("Toolhead:", homed)
            table.add_row(
                "Position:",
                f"X:{th.position[0]:.1f} Y:{th.position[1]:.1f} Z:{th.position[2]:.1f}"
            )

        # Fan speed
        if status.get('fan'):
            table.add_row("Fan:", f"{status['fan'].speed*100:.0f}%")

        return table

    def _update_status_loop(self):
        """Background thread to periodically update status data."""
        while self.status_running:
            try:
                new_status = self._query_status_data()

                with self.display_lock:
                    self.status_data = new_status

            except Exception:
                pass  # Silently continue on errors

            time.sleep(self.status_update_interval)

    def build_layout(self) -> Layout:
        """Build split-screen layout with console and status panels."""
        layout = Layout()

        # Split horizontally: 70% console, 30% status
        layout.split_column(
            Layout(name="console", ratio=70),
            Layout(name="status", ratio=30)
        )

        # Console panel (top)
        layout["console"].update(
            Panel(
                self.format_messages(),
                title="Klipper Console - Press Ctrl+C to exit",
                border_style="green"
            )
        )

        # Status panel (bottom)
        layout["status"].update(
            Panel(
                self.format_status_panel(),
                title="Printer Status",
                border_style="blue"
            )
        )

        return layout

    def display_console(self):
        """Display the console output."""
        current_time = time.time()

        # Rate limit display updates
        if current_time - self.last_display_time < self.display_interval:
            return

        self.last_display_time = current_time
        self.console.clear()

        if self.split_screen:
            # Split-screen mode: console + status
            layout = self.build_layout()
            self.console.print(layout)
        else:
            # Standard mode: console only
            self.console.print(Panel(
                self.format_messages(),
                title="Klipper Console - Press Ctrl+C to exit",
                border_style="green"
            ))

    def start(self):
        """Start the interactive console viewer."""
        self.running = True

        # Load historical messages
        self.console.print("[yellow]Loading historical console messages...[/yellow]")
        try:
            history = self.handlers.get_console_history(count=100)
            for msg in history:
                self.add_message(msg.message, msg.time, msg.type)
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load history: {e}[/yellow]")

        # Start WebSocket for real-time updates
        try:
            # Build WebSocket URL from client base_url
            base_url = self.handlers.client.base_url
            ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://") + "/websocket"

            from .moonraker.websocket_client import MoonrakerWebSocket
            self.ws_client = MoonrakerWebSocket(ws_url, self._on_ws_message)
            self.ws_client.connect()

            self.console.print("[green]Connected to real-time console output[/green]")
        except Exception as e:
            self.console.print(f"[yellow]Warning: WebSocket connection failed: {e}[/yellow]")
            self.console.print("[yellow]Continuing without real-time updates...[/yellow]")

        # Start status update thread if split-screen enabled
        if self.split_screen:
            self.console.print("[green]Starting status monitor...[/green]")
            self.status_running = True

            # Initial population
            self.status_data = self._query_status_data()

            # Start background thread
            self.status_thread = threading.Thread(
                target=self._update_status_loop,
                daemon=True
            )
            self.status_thread.start()

        self.console.print("[dim]Type G-code commands or press Ctrl+C to exit[/dim]\n")
        time.sleep(1)  # Give user time to read messages

        # Interactive input loop
        session = PromptSession(
            history=self.history,
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
            complete_while_typing=True
        )

        try:
            while self.running:
                # Display current console state
                self.display_console()

                # Get user input
                try:
                    command = session.prompt("\n█ > ")

                    if command.strip():
                        # Add command to display
                        self.add_message(f"> {command}", msg_type="command")

                        # Execute G-code command
                        try:
                            response = self.handlers.gcode(command)
                            if response:
                                self.add_message(response)
                        except Exception as e:
                            self.add_message(f"Error: {e}", msg_type="error")

                except KeyboardInterrupt:
                    break
                except EOFError:
                    break

        finally:
            self.stop()

    def _on_ws_message(self, msg_data: dict):
        """Callback for WebSocket messages."""
        self.add_message(
            msg_data.get("message", ""),
            msg_data.get("time"),
            msg_data.get("type", "response")
        )

    def stop(self):
        """Stop the console viewer."""
        # Stop status thread if running
        if self.status_thread and self.status_running:
            self.status_running = False
            self.status_thread.join(timeout=3.0)

        self.running = False
        if self.ws_client:
            self.ws_client.disconnect()
        self.console.print("\n[yellow]Exited console mode[/yellow]")
