#!/usr/bin/env python3
"""Diagnose RoboMaster S1 connection issues."""

import sys
import socket
import time

# SDK command port
CMD_PORT = 40923


def check_port_forward():
    """Check if ADB port forwarding is set up."""
    print("🔍 Checking ADB port forwarding...")
    print()

    import subprocess

    result = subprocess.run(
        ["adb", "forward", "--list"], capture_output=True, text=True
    )

    if result.stdout.strip():
        print("✅ Active port forwards:")
        for line in result.stdout.strip().split("\n"):
            print(f"   {line}")
        return True
    else:
        print("❌ No port forwards active!")
        print()
        print("🔧 Fix: Run 'python adb_bridge.py forward'")
        return False


def test_tcp_connection(host="127.0.0.1", port=CMD_PORT, timeout=5):
    """Test if we can open a TCP connection to the robot."""
    print(f"\n🔍 Testing TCP connection to {host}:{port}...")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        print(f"✅ TCP connection successful!")

        sock.settimeout(5)

        # 1. SDK-Modus AKTIVIEREN (Pflicht als allererstes!)
        print("\n📡 Enabling SDK mode ('command;')...")
        sock.send(b"command;")
        resp = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        print(f"📥 Response: '{resp}'")   # erwartet: 'ok'

        if "ok" not in resp.lower():
            print("⚠️  SDK-Modus wurde NICHT aktiviert – Roboter antwortet nicht mit 'ok'.")
            sock.close()
            return False

        # 2. Jetzt erst version abfragen
        print("\n📡 Sending version command ('version;')...")
        sock.send(b"version;")
        resp = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        print(f"📥 Response: '{resp}'")

        # 3. Sauber wieder aus dem SDK-Modus gehen
        sock.send(b"quit;")

        sock.close()
        return True

    except socket.timeout:
        print(f"❌ Connection timed out after {timeout}s")
        return False
    except ConnectionRefusedError:
        print(f"❌ Connection refused - port {port} not open")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_sdk_connection(host="127.0.0.1"):
    """Test connection using the SDK."""
    print(f"\n🔍 Testing SDK connection to {host}...")
    print()

    try:
        from robomaster import robot, config
    except ImportError:
        print("❌ robomaster SDK not installed!")
        return False

    ep_robot = None

    try:
        print("   Creating Robot object...")
        ep_robot = robot.Robot()

        print("   Setting ROBOT_IP_ADDR...")
        config.ROBOT_IP_ADDR = host

        print("   Calling initialize(conn_type='sta')...")
        ep_robot.initialize(conn_type="sta")

        print("✅ SDK connection established!")

        # Try getting version
        print("\n📋 Querying robot info...")
        try:
            version = ep_robot.get_version()
            print(f"   Version: {version}")
        except Exception as e:
            print(f"   Version: failed ({e})")

        return True

    except Exception as e:
        print(f"❌ SDK connection failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        if ep_robot:
            print("\n📴 Cleaning up...")
            try:
                ep_robot.close()
            except Exception:
                pass


def main():
    print("=" * 60)
    print("🤖 RoboMaster S1 Connection Diagnostics")
    print("=" * 60)
    print()

    if not check_port_forward():
        print("\n⚠️  Port forwarding not set up. Set it up first.")
        return 1

    tcp_ok = test_tcp_connection("127.0.0.1", CMD_PORT)

    if tcp_ok:
        print("\n" + "=" * 60)
        print("✅ Plaintext-SDK funktioniert!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Verbindung steht, aber SDK-Modus antwortet nicht")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
