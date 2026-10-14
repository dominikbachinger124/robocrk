#!/usr/bin/env python3
"""ADB Bridge for RoboMaster S1 USB Connection.

Since the S1 hack reenables ADB by default (disabling RNDIS),
we use ADB port forwarding to connect the SDK via USB.

Typical connection flow:
1. Connect S1 via USB cable
2. Run this script to forward ports
3. Use '127.0.0.1' as the robot IP in SDK scripts
"""

import subprocess
import sys
import time
import argparse


# RoboMaster SDK ports
SDK_PORTS = [40923, 40924, 40925]  # cmd, video, audio


def run_adb_command(args: list) -> tuple:
    """Run an ADB command and return (success, output, error)."""
    cmd = ["adb"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return (result.returncode == 0, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (False, "", "Command timed out")
    except FileNotFoundError:
        return (False, "", "ADB not found. Install Android SDK platform-tools.")


def check_device() -> bool:
    """Check if S1 is connected via ADB."""
    print("🔍 Checking ADB devices...")
    success, stdout, stderr = run_adb_command(["devices"])

    if not success:
        print(f"❌ ADB error: {stderr}")
        return False

    lines = stdout.strip().split("\n")
    devices = [l for l in lines if "\tdevice" in l]

    if not devices:
        print("❌ No devices found. Is the S1 connected via USB?")
        print(f"   ADB output: {stdout}")
        return False

    print(f"✅ Found device: {devices[0].split()[0]}")
    return True


def forward_ports() -> bool:
    """Forward SDK ports via ADB."""
    print("\n🔌 Setting up port forwarding...")

    for port in SDK_PORTS:
        # Forward local port to remote port on device
        success, stdout, stderr = run_adb_command(
            ["forward", f"tcp:{port}", f"tcp:{port}"]
        )

        if not success:
            print(f"❌ Failed to forward port {port}: {stderr}")
            return False

        print(f"   ✅ Port {port} -> {port}")

    print("\n✅ Port forwarding active!")
    return True


def remove_forwarding() -> bool:
    """Remove all ADB port forwarding."""
    print("\n🧹 Removing port forwarding...")
    success, stdout, stderr = run_adb_command(["forward", "--remove-all"])

    if not success:
        print(f"⚠️  Error removing forwards: {stderr}")
        return False

    print("✅ Port forwarding removed")
    return True


def list_forwards():
    """List active port forwards."""
    success, stdout, stderr = run_adb_command(["forward", "--list"])

    if not success:
        print(f"❌ Error: {stderr}")
        return

    if stdout.strip():
        print("📋 Active port forwards:")
        print(stdout)
    else:
        print("📋 No active port forwards")


def check_adb_root() -> bool:
    """Check if ADB has root access on the device."""
    print("🔍 Checking ADB root access...")
    success, stdout, stderr = run_adb_command(["shell", "whoami"])

    if not success:
        print(f"❌ ADB shell error: {stderr}")
        return False

    user = stdout.strip()
    if user == "root":
        print(f"✅ ADB running as root")
        return True
    else:
        print(f"⚠️  ADB running as '{user}' (not root)")
        print("   Some features may be limited")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="ADB Bridge for RoboMaster S1 USB Connection"
    )
    parser.add_argument(
        "action",
        choices=["forward", "remove", "list", "check", "setup"],
        default="setup",
        nargs="?",
        help="Action to perform",
    )

    args = parser.parse_args()

    print("=" * 50)
    print("🤖 RoboMaster S1 ADB Bridge")
    print("=" * 50)
    print()

    if args.action == "check":
        check_device()
        check_adb_root()
        list_forwards()

    elif args.action == "forward":
        if check_device():
            forward_ports()
            print("\n💡 Use '127.0.0.1' as the robot IP in SDK scripts")

    elif args.action == "remove":
        remove_forwarding()

    elif args.action == "list":
        list_forwards()

    elif args.action == "setup":
        if not check_device():
            sys.exit(1)

        check_adb_root()
        list_forwards()

        print()
        if forward_ports():
            print()
            print("=" * 50)
            print("✅ Setup complete!")
            print("=" * 50)
            print()
            print("💡 Next steps:")
            print("   1. Use '127.0.0.1' as the robot IP")
            print("   2. Run: ./venv/bin/python test_connection.py --ip 127.0.0.1")
            print()
            print("📝 Note: Keep this terminal open while using the SDK.")
            print("   Press Ctrl+C to remove port forwarding when done.")
            print()

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n👋 Shutting down...")
                remove_forwarding()


if __name__ == "__main__":
    main()
