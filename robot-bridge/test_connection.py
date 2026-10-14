#!/usr/bin/env python3
"""Test connection to DJI RoboMaster S1.

This script attempts to connect to the robot using the robomaster SDK
and retrieve basic information.
"""

import sys
import time
import argparse
import traceback

try:
    from robomaster import robot, config
except ImportError as e:
    print(f"Error: robomaster SDK not installed. {e}")
    print("Run: pip install robomaster")
    sys.exit(1)


def test_connection(robot_ip: str = None, timeout: int = 10) -> bool:
    """Test connection to RoboMaster S1.

    Args:
        robot_ip: IP address of the robot. If None, uses auto-discovery.
        timeout: Connection timeout in seconds.

    Returns:
        True if connection successful, False otherwise.
    """
    print(f"🤖 RoboMaster S1 Connection Test")
    print(f"{'=' * 40}")
    print(f"Target IP: {robot_ip or 'Auto-discovery'}")
    print(f"Timeout: {timeout}s")
    print()

    ep_robot = None

    try:
        # Initialize robot
        print("📡 Initializing robot connection...")
        print(f"   Using conn_type='sta' (station mode)")

        ep_robot = robot.Robot()

        # Try to initialize with proper configuration
        # For USB/ADB forwarded connection, use local address
        if robot_ip == "127.0.0.1":
            print("   Configuring for local port forwarding (ADB)...")
            # Set local address for forwarded connection
            config.ROBOT_IP_ADDR = robot_ip

        print("   Calling robot.initialize()...")
        ep_robot.initialize(conn_type="sta")

        print("✅ Connected to robot!")
        print()

        # Get robot version
        try:
            version = ep_robot.get_version()
            print(f"📋 Robot Version: {version}")
        except Exception as e:
            print(f"⚠️  Could not get version: {e}")

        # Get robot SN
        try:
            sn = ep_robot.get_sn()
            print(f"📋 Robot SN: {sn}")
        except Exception as e:
            print(f"⚠️  Could not get SN: {e}")

        # Get battery level
        try:
            battery = ep_robot.battery.get_battery()
            print(f"🔋 Battery: {battery}%")
        except Exception as e:
            print(f"⚠️  Could not get battery: {e}")

        print()
        print("✅ Connection test PASSED")
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("🔍 Debug traceback:")
        traceback.print_exc()
        print()
        print("🔧 Troubleshooting:")
        print("  1. Ensure robot is powered on and booted (2 chimes = hacked)")
        print("  2. Check USB cable is connected to Micro USB port on controller")
        print("  3. Verify ADB port forwarding is active: adb forward --list")
        print("  4. Try: adb shell (to verify ADB connection works)")
        print("  5. Check if another program is already connected to the SDK")
        print()
        return False

    finally:
        if ep_robot is not None:
            print()
            print("📴 Cleaning up connection...")
            try:
                # Give the SDK a moment to stabilize before closing
                time.sleep(0.5)
                ep_robot.close()
                print("   ✅ Connection closed cleanly")
            except Exception as e:
                # Suppress cleanup errors as they're usually secondary
                print(f"   ⚠️  Cleanup warning (can be ignored): {type(e).__name__}")


def test_connection_simple(robot_ip: str = "127.0.0.1", timeout: int = 10) -> bool:
    """Simplified connection test that handles the SDK quirks better."""
    print(f"🤖 RoboMaster S1 Connection Test (Simple)")
    print(f"{'=' * 50}")
    print(f"Target IP: {robot_ip}")
    print()

    ep_robot = None

    try:
        print("📡 Creating robot object...")
        ep_robot = robot.Robot()

        print("📡 Initializing connection...")
        # Set the robot IP in config BEFORE initializing
        if robot_ip:
            config.ROBOT_IP_ADDR = robot_ip

        # The SDK uses a default timeout internally
        ep_robot.initialize(conn_type="sta")

        # If we get here, connection was successful
        print("✅ Connected!")

        # Small delay for SDK to fully initialize
        time.sleep(1)

        # Try to get version
        print()
        print("📋 Getting robot info...")
        try:
            version = ep_robot.get_version()
            print(f"   Version: {version}")
        except Exception as e:
            print(f"   Version: unavailable ({e})")

        try:
            sn = ep_robot.get_sn()
            print(f"   SN: {sn}")
        except Exception as e:
            print(f"   SN: unavailable ({e})")

        try:
            battery = ep_robot.battery.get_battery()
            print(f"   Battery: {battery}%")
        except Exception as e:
            print(f"   Battery: unavailable ({e})")

        print()
        print("✅ Connection test PASSED!")
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        traceback.print_exc()
        return False

    finally:
        if ep_robot is not None:
            print()
            print("📴 Closing connection...")
            try:
                # Try to close gracefully
                ep_robot.close()
                print("   Closed")
            except Exception:
                # Ignore cleanup errors
                pass


def list_available_robots(timeout: int = 5):
    """Scan for available robots on the network."""
    print(f"🔍 Scanning for robots (timeout: {timeout}s)...")
    print()

    try:
        from robomaster import util

        # This will broadcast and look for robots
        util.scan_robot(timeout=timeout)

    except Exception as e:
        print(f"❌ Scan failed: {e}")
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description="Test connection to DJI RoboMaster S1")
    parser.add_argument(
        "--ip",
        type=str,
        default="127.0.0.1",
        help="Robot IP address (default: 127.0.0.1 for ADB forwarding)",
    )
    parser.add_argument("--scan", action="store_true", help="Scan for available robots")
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Connection timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--simple", action="store_true", help="Use simple connection method"
    )

    args = parser.parse_args()

    if args.scan:
        list_available_robots(args.timeout)
    elif args.simple:
        success = test_connection_simple(args.ip, args.timeout)
        sys.exit(0 if success else 1)
    else:
        success = test_connection(args.ip, args.timeout)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
