#!/usr/bin/env python3
"""Low-level connection to RoboMaster S1 using plaintext protocol.

The official SDK has issues with the hacked S1 firmware.
This script uses the plaintext protocol directly via TCP.
"""

import socket
import time
import sys

CMD_PORT = 40923
BUFFER_SIZE = 1024
TIMEOUT = 5


class PlaintextConnection:
    """Direct plaintext protocol connection to S1."""

    def __init__(self, host="127.0.0.1", port=CMD_PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        """Connect to the robot."""
        print(f"📡 Connecting to {self.host}:{self.port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(TIMEOUT)
        self.sock.connect((self.host, self.port))
        print("✅ Connected!")
        return True

    def send_command(self, command: str) -> str:
        """Send a command and get response."""
        if not self.sock:
            raise RuntimeError("Not connected")

        # Commands must end with semicolon
        if not command.endswith(";"):
            command += ";"

        self.sock.send(command.encode())

        # Receive response
        self.sock.settimeout(TIMEOUT)
        response = self.sock.recv(BUFFER_SIZE).decode("utf-8", errors="ignore")
        return response.strip()

    def close(self):
        """Close connection."""
        if self.sock:
            self.sock.close()
            self.sock = None
            print("📴 Disconnected")


def test_connection(host="127.0.0.1"):
    """Test connection using plaintext protocol."""
    print("=" * 60)
    print("🤖 RoboMaster S1 Plaintext Connection Test")
    print("=" * 60)
    print()

    conn = PlaintextConnection(host)

    try:
        conn.connect()

        print()
        print("📋 Testing commands...")
        print()

        # Test version command
        print("1. version")
        response = conn.send_command("version")
        print(f"   Response: {response}")

        # Test robot mode
        print("2. robot mode")
        response = conn.send_command("robot mode")
        print(f"   Response: {response}")

        # Test chassis
        print("3. chassis wheel (check chassis)")
        response = conn.send_command("chassis wheel")
        print(f"   Response: {response}")

        # Test gimbal
        print("4. gimbal moveto (check gimbal)")
        response = conn.send_command("gimbal moveto pitch 0 yaw 0")
        print(f"   Response: {response}")

        # Test battery
        print("5. battery ?")
        try:
            response = conn.send_command("battery ?")
            print(f"   Response: {response}")
        except Exception as e:
            print(f"   Error: {e}")

        print()
        print("=" * 60)
        print("✅ Plaintext connection working!")
        print("=" * 60)
        print()
        print("💡 You can now control the robot using plaintext commands:")
        print("   - chassis move x 0.5    (move forward 0.5m)")
        print("   - chassis move y 0.3    (move right 0.3m)")
        print("   - gimbal moveto pitch 0 yaw 0")
        print()

        return conn  # Return connection for interactive use

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        conn.close()
        return None


def interactive_mode(conn):
    """Interactive command mode."""
    print()
    print("🎮 Interactive Mode")
    print("Type commands (or 'quit' to exit)")
    print("Examples: 'version', 'robot mode', 'chassis wheel'")
    print()

    while True:
        try:
            cmd = input("> ").strip()
            if cmd.lower() in ("quit", "exit", "q"):
                break
            if not cmd:
                continue

            response = conn.send_command(cmd)
            print(f"  {response}")

        except KeyboardInterrupt:
            print("\nUse 'quit' to exit")
        except Exception as e:
            print(f"  Error: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Low-level plaintext connection to S1")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Robot host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive mode after connection",
    )

    args = parser.parse_args()

    conn = test_connection(args.host)

    if conn and args.interactive:
        try:
            interactive_mode(conn)
        finally:
            conn.close()
    elif conn:
        conn.close()


if __name__ == "__main__":
    main()
