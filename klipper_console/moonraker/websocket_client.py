"""WebSocket client for real-time Moonraker updates."""

import json
import threading
from typing import Callable, Optional
from websocket import WebSocketApp


class MoonrakerWebSocket:
    """WebSocket client for Moonraker real-time updates."""

    def __init__(self, url: str, on_message: Callable[[dict], None]):
        """
        Initialize WebSocket client.

        Args:
            url: WebSocket URL (e.g., "ws://localhost:7125/websocket")
            on_message: Callback for received messages
        """
        self.url = url
        self.on_message_callback = on_message
        self.ws = None
        self.thread = None
        self.connected = False

    def connect(self):
        """Connect to WebSocket."""
        self.ws = WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

        # Run WebSocket in background thread
        self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.thread.start()

    def _on_open(self, ws):
        """Handle WebSocket connection open."""
        self.connected = True

        # Subscribe to gcode_response events
        subscribe_msg = {
            "jsonrpc": "2.0",
            "method": "printer.objects.subscribe",
            "params": {
                "objects": {
                    "gcode_move": None,
                    "toolhead": None
                }
            },
            "id": 1
        }
        ws.send(json.dumps(subscribe_msg))

    def _on_message(self, ws, message):
        """Handle received WebSocket message."""
        try:
            data = json.loads(message)

            # Check for gcode_response in notify_gcode_response
            if data.get("method") == "notify_gcode_response":
                params = data.get("params", [])
                if params:
                    # Call user callback with message
                    self.on_message_callback({
                        "message": params[0],
                        "time": data.get("time", 0),
                        "type": "response"
                    })

        except json.JSONDecodeError:
            pass

    def _on_error(self, ws, error):
        """Handle WebSocket error."""
        self.connected = False

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close."""
        self.connected = False

    def disconnect(self):
        """Disconnect from WebSocket."""
        if self.ws:
            self.ws.close()
            self.connected = False
