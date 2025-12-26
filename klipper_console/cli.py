"""CLI entry point."""

import argparse
import sys

from .moonraker import MoonrakerClient
from .handlers import Handlers
from .registry import CommandRegistry
from .shell import KlipperShell
from .render import print_error


def main():
    """Main entry point for klipper-console."""
    parser = argparse.ArgumentParser(
        description="Terminal-native CLI for Klipper via Moonraker"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:7125",
        help="Moonraker URL (default: http://localhost:7125)"
    )
    parser.add_argument(
        "--api-key",
        help="API key for authentication"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Request timeout in seconds (default: 120.0)"
    )
    parser.add_argument(
        "--split-screen",
        action="store_true",
        help="Enable split-screen mode in console viewer (console + status)"
    )

    args = parser.parse_args()

    # Create Moonraker client
    client = MoonrakerClient(
        base_url=args.url,
        api_key=args.api_key,
        timeout=args.timeout
    )

    try:
        # Connect to Moonraker
        client.connect()

        # Create handlers and registry
        handlers = Handlers(client)
        handlers.split_screen_enabled = args.split_screen
        registry = CommandRegistry(handlers)

        # Create and run shell
        shell = KlipperShell(registry)
        shell.run()

    except ConnectionError as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
