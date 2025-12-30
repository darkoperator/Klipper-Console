"""Interactive REPL shell."""

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from .parser import parse_command
from .registry import CommandRegistry
from .completion import KlipperCompleter
from .render import render_result, print_error, console


class KlipperShell:
    """Interactive shell for Klipper console."""

    def __init__(self, registry: CommandRegistry):
        """
        Initialize shell.

        Args:
            registry: Command registry
        """
        self.registry = registry
        self.history = InMemoryHistory()
        self.completer = KlipperCompleter(registry)
        self.session = PromptSession(
            history=self.history,
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
            complete_while_typing=True
        )

    def run(self):
        """Run the interactive shell loop."""
        console.print("[bold green]Klipper Console v0.1.0[/bold green]")
        console.print("[dim]Author: Carlos Perez <carlos_perez@darkoperator.com>[/dim]")
        console.print("Type 'help' for available commands, 'exit' to quit.\n")

        while True:
            try:
                # Get user input
                line = self.session.prompt("klipper> ")

                # Parse command
                parsed = parse_command(line)
                if not parsed:
                    continue

                # Execute command
                try:
                    result = self.registry.execute(parsed)

                    # Check for exit signal
                    if result == "__EXIT__":
                        console.print("[dim]Goodbye![/dim]")
                        break

                    # Render result
                    render_result(result)

                    # Add spacing after output
                    if result is not None:
                        console.print()

                except KeyError as e:
                    print_error(str(e))
                except ValueError as e:
                    print_error(str(e))
                except Exception as e:
                    print_error(f"Command failed: {e}")

            except KeyboardInterrupt:
                # Ctrl+C - cancel current line
                continue
            except EOFError:
                # Ctrl+D - exit
                console.print("\n[dim]Goodbye![/dim]")
                break
            except Exception as e:
                print_error(f"Unexpected error: {e}")


__all__ = ["KlipperShell"]
