#!/usr/bin/env python3
"""Test if movement commands work (even if responses are empty)."""

import socket
import time
import sys

CMD_PORT = 40923


def send_cmd(sock, cmd):
    """Send command (responses may be empty from hacked S1)."""
    if not cmd.endswith(";"):
        cmd += ";"
    sock.send(cmd.encode())
    time.sleep(0.1)  # Brief delay
    try:
        return sock.recv(1024).decode("utf-8", errors="ignore").strip()
    except:
        return ""


def main():
    print("=" * 60)
    print("🤖 Movement Test (Hacked S1)")
    print("=" * 60)
    print()

    # Connect
    print("📡 Connecting...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect(("127.0.0.1", CMD_PORT))
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return 1

    print("✅ Connected!")
    print()

    try:
        # Test 1: Gimbal movement (safe)
        print("🎮 Test 1: Gimbal movement")
        print("   Command: gimbal moveto p 10 y 20")
        send_cmd(sock, "gimbal moveto p 10 y 20 vp 100 vy 100")
        time.sleep(2)

        print("   Command: gimbal moveto p 0 y 0")
        send_cmd(sock, "gimbal moveto p 0 y 0 vp 100 vy 100")
        time.sleep(2)
        print("   ✅ Gimbal should have moved")
        print()

        # Test 2: LED control
        print("💡 Test 2: LED control")
        print("   Command: led green")
        send_cmd(sock, "led control comp top_all r 0 g 255 b 0")
        time.sleep(0.5)
        print("   Command: led red")
        send_cmd(sock, "led control comp top_all r 255 g 0 b 0")
        time.sleep(0.5)
        print("   Command: led off")
        send_cmd(sock, "led control comp top_all r 0 g 0 b 0")
        print("   ✅ LEDs should have changed")
        print()

        # Test 3: Small chassis movement (very small, safe)
        print("🏎️  Test 3: Chassis movement (SMALL)")
        print("   ⚠️  Make sure robot has space!")
        print("   Command: chassis move x 0.1 (forward 10cm)")
        send_cmd(sock, "chassis move x 0.1 vxy 0.2")
        time.sleep(2)
        print("   Command: chassis move x -0.1 (back 10cm)")
        send_cmd(sock, "chassis move x -0.1 vxy 0.2")
        time.sleep(2)
        print("   ✅ Chassis should have moved slightly")
        print()

        # Test 4: Wheel speed (momentary)
        print("🏎️  Test 4: Wheel speed test (momentary)")
        print("   Command: chassis wheel w1 100 w2 100 w3 100 w4 100")
        send_cmd(sock, "chassis wheel w1 100 w2 100 w3 100 w4 100")
        time.sleep(0.5)
        print("   Command: chassis wheel w1 0 w2 0 w3 0 w4 0")
        send_cmd(sock, "chassis wheel w1 0 w2 0 w3 0 w4 0")
        print("   ✅ Wheels should have spun briefly")
        print()

        print("=" * 60)
        print("✅ All tests sent!")
        print("=" * 60)
        print()
        print("Did the robot move?")
        print("  - If YES: The plaintext protocol works!")
        print("  - If NO: The hack may need different protocol")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        sock.close()
        print()
        print("📴 Disconnected")

    return 0


if __name__ == "__main__":
    sys.exit(main())
