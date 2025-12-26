"""Moonraker HTTP client with authentication support."""

import httpx
from typing import Any, Optional


class MoonrakerClient:
    """HTTP client for Moonraker API."""

    def __init__(
        self,
        base_url: str = "http://localhost:7125",
        api_key: Optional[str] = None,
        timeout: float = 120.0
    ):
        """
        Initialize Moonraker client.

        Args:
            base_url: Moonraker base URL (default: http://localhost:7125)
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds (default: 120.0)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()

    def connect(self):
        """Establish connection to Moonraker."""
        headers = {}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout
        )

        # Verify connection
        try:
            self.get_server_info()
        except Exception as e:
            self.close()
            raise ConnectionError(f"Failed to connect to Moonraker at {self.base_url}: {e}")

    def close(self):
        """Close the client connection."""
        if self._client:
            self._client.close()
            self._client = None

    def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """
        Make HTTP request to Moonraker.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request

        Returns:
            Response data as dict

        Raises:
            RuntimeError: If client is not connected
            httpx.HTTPError: On HTTP errors
        """
        if not self._client:
            raise RuntimeError("Client not connected. Call connect() first.")

        response = self._client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        data = response.json()

        # Moonraker wraps responses in {"result": ...}
        if "result" in data:
            return data["result"]

        # Error responses have {"error": {...}}
        if "error" in data:
            error = data["error"]
            raise RuntimeError(f"Moonraker error: {error.get('message', error)}")

        return data

    def get(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make GET request."""
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make POST request."""
        return self._request("POST", endpoint, **kwargs)

    # Server info

    def get_server_info(self) -> dict[str, Any]:
        """Get Moonraker server information."""
        return self.get("/server/info")

    # Printer object queries

    def list_objects(self) -> list[str]:
        """List all available printer objects."""
        result = self.get("/printer/objects/list")
        return result.get("objects", [])

    def query_objects(self, objects: dict[str, Optional[list[str]]] = None) -> dict[str, Any]:
        """
        Query printer object state.

        Args:
            objects: Dict mapping object names to optional list of fields.
                    If fields is None, all fields are returned.
                    Example: {"fan": None, "extruder": ["temperature", "target"]}

        Returns:
            Dict with "eventtime" and "status" keys
        """
        if objects is None:
            objects = {}

        # Build query string
        params = {}
        for obj, fields in objects.items():
            if fields:
                params[obj] = ",".join(fields)
            else:
                params[obj] = None

        result = self.get("/printer/objects/query", params=params)
        return result

    # G-code execution

    def run_gcode(self, script: str) -> str:
        """
        Execute G-code command.

        Args:
            script: G-code command or script to execute

        Returns:
            Command output/response
        """
        result = self.post("/printer/gcode/script", params={"script": script})
        return result

    # Helper methods for common queries

    def get_printer_info(self) -> dict[str, Any]:
        """Get printer info (Klipper state)."""
        return self.get("/printer/info")

    def get_endstops(self) -> dict[str, Any]:
        """Query endstop states."""
        return self.get("/printer/query_endstops/status")

    def emergency_stop(self):
        """Emergency stop the printer."""
        return self.post("/printer/emergency_stop")

    def restart_klipper(self):
        """Restart Klipper firmware."""
        return self.post("/printer/restart")

    def firmware_restart(self):
        """Restart Klipper firmware (firmware_restart)."""
        return self.post("/printer/firmware_restart")

    def get_gcode_help(self) -> dict[str, str]:
        """
        Get help information for all available G-code commands.

        Returns:
            Dictionary mapping command names to help strings
        """
        result = self.get("/printer/gcode/help")
        return result

    def get_gcode_store(self, count: int = 100) -> list:
        """
        Get historical G-code responses from the store.

        Args:
            count: Number of messages to retrieve (default: 100)

        Returns:
            List of historical console messages
        """
        # Query the gcode_store object
        result = self.query_objects({"gcode_store": None})
        store_data = result.get("status", {}).get("gcode_store", {})

        # Get messages (Moonraker stores messages as a list)
        messages = store_data.get("gcode_store", [])

        # Return last N messages
        if len(messages) > count:
            return messages[-count:]
        return messages

    # File management

    def list_files(self, path: str = "gcodes") -> dict[str, Any]:
        """
        List files in a directory.

        Args:
            path: Directory path (default: gcodes)

        Returns:
            Dictionary with file listing
        """
        return self.get(f"/server/files/list", params={"path": path})

    def get_file_metadata(self, filename: str) -> dict[str, Any]:
        """
        Get metadata for a specific file.

        Args:
            filename: File name (path relative to gcodes directory)

        Returns:
            File metadata dictionary
        """
        return self.get(f"/server/files/metadata", params={"filename": filename})

    def delete_file(self, filename: str) -> dict[str, Any]:
        """
        Delete a file.

        Args:
            filename: File name (path relative to gcodes directory)

        Returns:
            Result dictionary
        """
        # URL encode the filename
        import urllib.parse
        encoded_name = urllib.parse.quote(filename, safe='')
        return self._request("DELETE", f"/server/files/gcodes/{encoded_name}")

    def move_file(self, source: str, dest: str) -> dict[str, Any]:
        """
        Move a file.

        Args:
            source: Source file path
            dest: Destination file path

        Returns:
            Result dictionary
        """
        return self.post("/server/files/move", json={
            "source": f"gcodes/{source}",
            "dest": f"gcodes/{dest}"
        })

    def copy_file(self, source: str, dest: str) -> dict[str, Any]:
        """
        Copy a file.

        Args:
            source: Source file path
            dest: Destination file path

        Returns:
            Result dictionary
        """
        return self.post("/server/files/copy", json={
            "source": f"gcodes/{source}",
            "dest": f"gcodes/{dest}"
        })

    def start_print(self, filename: str) -> dict[str, Any]:
        """
        Start printing a file.

        Args:
            filename: File name (path relative to gcodes directory)

        Returns:
            Result dictionary
        """
        return self.post("/printer/print/start", json={"filename": filename})

    # Directory management

    def create_directory(self, path: str) -> dict[str, Any]:
        """
        Create a new directory.

        Args:
            path: Directory path (e.g., "gcodes/my_folder")

        Returns:
            Result dictionary with created directory info
        """
        return self.post("/server/files/directory", json={"path": path})

    def list_directory(self, path: str = "gcodes", extended: bool = True) -> dict[str, Any]:
        """
        List directory contents.

        Args:
            path: Directory path (default: "gcodes")
            extended: Include extended metadata (default: True)

        Returns:
            Dictionary with dirs, files, disk_usage, root_info
        """
        params = {"path": path, "extended": str(extended).lower()}
        return self.get("/server/files/directory", params=params)

    # File upload/download

    def upload_file(
        self,
        local_path: str,
        remote_path: str = "gcodes",
        filename: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Upload a file to the printer.

        Args:
            local_path: Local file path to upload
            remote_path: Remote directory path (default: "gcodes")
            filename: Optional custom filename (default: use local filename)

        Returns:
            Result dictionary with uploaded file info
        """
        import os
        from pathlib import Path

        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file not found: {local_path}")

        # Determine filename
        if filename is None:
            filename = Path(local_path).name

        # Prepare multipart form data
        with open(local_path, 'rb') as f:
            files = {'file': (filename, f, 'application/octet-stream')}
            data = {
                'root': remote_path.split('/')[0] if '/' in remote_path else remote_path,
                'path': '/'.join(remote_path.split('/')[1:]) if '/' in remote_path else '',
            }

            # Use httpx multipart upload
            if not self._client:
                raise RuntimeError("Client not connected. Call connect() first.")

            response = self._client.post('/server/files/upload', files=files, data=data)
            response.raise_for_status()

            result = response.json()
            if "result" in result:
                return result["result"]
            if "error" in result:
                raise RuntimeError(f"Upload failed: {result['error']}")
            return result

    def download_file(self, remote_path: str, local_path: str) -> None:
        """
        Download a file from the printer.

        Args:
            remote_path: Remote file path (e.g., "gcodes/test.gcode")
            local_path: Local destination path
        """
        import urllib.parse
        from pathlib import Path

        # URL encode the path
        encoded_path = urllib.parse.quote(remote_path, safe='')
        endpoint = f"/server/files/{encoded_path}"

        try:
            if not self._client:
                raise RuntimeError("Client not connected. Call connect() first.")

            response = self._client.get(endpoint)
            response.raise_for_status()

            # Ensure local directory exists
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(local_path, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            raise RuntimeError(f"Download failed: {e}")
