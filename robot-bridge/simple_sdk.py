#!/usr/bin/env python3
"""Simple SDK wrapper using plaintext protocol for hacked S1.

This provides a simplified API that works with the hacked S1 firmware
since the official SDK has compatibility issues.
"""

import socket
import time
import threading
from typing import Optional, Callable

CMD_PORT = 40923
VIDEO_PORT = 40924
AUDIO_PORT = 40925
BUFFER_SIZE = 1024
DEFAULT_TIMEOUT = 5


class SimpleRobot:
    """Simplified robot control for hacked S1."""

    def __init__(self, host: str = "127.0.0.1"):
        self.host = host
        self.cmd_sock: Optional[socket.socket] = None
        self.video_sock: Optional[socket.socket] = None
        self._connected = False

    def connect(self, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Connect to the robot."""
        print(f"📡 Connecting to {self.host}...")

        try:
            # Connect to command port
            self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cmd_sock.settimeout(timeout)
            self.cmd_sock.connect((self.host, CMD_PORT))

            self._connected = True
            print("✅ Connected to command port")

            # Get version to verify connection
            version = self.get_version()
            print(f"   Version: {version}")

            return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.close()
            return False

    def close(self):
        """Close all connections."""
        self._connected = False

        if self.cmd_sock:
            try:
                self.cmd_sock.close()
            except:
                pass
            self.cmd_sock = None

        if self.video_sock:
            try:
                self.video_sock.close()
            except:
                pass
            self.video_sock = None

        print("📴 Disconnected")

    def _send(self, command: str) -> str:
        """Send command and return response."""
        if not self.cmd_sock or not self._connected:
            raise RuntimeError("Not connected")

        # Ensure command ends with semicolon
        if not command.endswith(";"):
            command += ";"

        self.cmd_sock.send(command.encode())

        # Receive response
        self.cmd_sock.settimeout(DEFAULT_TIMEOUT)
        response = self.cmd_sock.recv(BUFFER_SIZE).decode("utf-8", errors="ignore")
        return response.strip()

    # ========== Robot Info ==========

    def get_version(self) -> str:
        """Get robot firmware version."""
        return self._send("version")

    def get_sn(self) -> str:
        """Get robot serial number."""
        return self._send("robot sn ?")

    def get_mode(self) -> str:
        """Get robot mode."""
        return self._send("robot mode ?")

    def set_mode(self, mode: str = "free") -> str:
        """Set robot mode (free, chassis_lead, gimbal_lead)."""
        return self._send(f"robot mode {mode}")

    # ========== Chassis Control ==========

    def chassis_move(
        self, x: float = 0, y: float = 0, z: float = 0, speed: float = 1.0
    ) -> str:
        """
        Move chassis.

        Args:
            x: Forward/backward distance in meters (positive = forward)
            y: Left/right distance in meters (positive = right)
            z: Rotation in degrees (positive = clockwise)
            speed: Movement speed (0-1)
        """
        return self._send(f"chassis move x {x} y {y} z {z} vxy {speed}")

    def chassis_wheel(self, w1: int = 0, w2: int = 0, w3: int = 0, w4: int = 0) -> str:
        """
        Control individual wheels.

        Args:
            w1: Front left wheel speed (-1000 to 1000)
            w2: Front right wheel speed (-1000 to 1000)
            w3: Rear left wheel speed (-1000 to 1000)
            w4: Rear right wheel speed (-1000 to 1000)
        """
        return self._send(f"chassis wheel w1 {w1} w2 {w2} w3 {w3} w4 {w4}")

    def chassis_speed(self, x: float = 0, y: float = 0, z: float = 0) -> str:
        """
        Set chassis speed.

        Args:
            x: Forward speed m/s
            y: Right speed m/s
            z: Rotation speed deg/s
        """
        return self._send(f"chassis speed x {x} y {y} z {z}")

    def get_chassis_position(self) -> str:
        """Get chassis position."""
        return self._send("chassis position ?")

    def get_chassis_attitude(self) -> str:
        """Get chassis attitude (pitch, roll, yaw)."""
        return self._send("chassis attitude ?")

    def get_chassis_status(self) -> str:
        """Get chassis status."""
        return self._send("chassis status ?")

    # ========== Gimbal Control ==========

    def gimbal_moveto(
        self,
        pitch: float = 0,
        yaw: float = 0,
        pitch_speed: float = 30,
        yaw_speed: float = 30,
    ) -> str:
        """
        Move gimbal to absolute position.

        Args:
            pitch: Pitch angle in degrees (-20 to 35)
            yaw: Yaw angle in degrees (-250 to 250)
            pitch_speed: Pitch movement speed (0-540)
            yaw_speed: Yaw movement speed (0-540)
        """
        return self._send(
            f"gimbal moveto p {pitch} y {yaw} vp {pitch_speed} vy {yaw_speed}"
        )

    def gimbal_move(
        self,
        pitch: float = 0,
        yaw: float = 0,
        pitch_speed: float = 30,
        yaw_speed: float = 30,
    ) -> str:
        """
        Move gimbal relative to current position.

        Args:
            pitch: Pitch change in degrees
            yaw: Yaw change in degrees
            pitch_speed: Pitch movement speed
            yaw_speed: Yaw movement speed
        """
        return self._send(
            f"gimbal move p {pitch} y {yaw} vp {pitch_speed} vy {yaw_speed}"
        )

    def gimbal_speed(self, pitch_speed: float = 0, yaw_speed: float = 0) -> str:
        """
        Set gimbal rotation speed.

        Args:
            pitch_speed: Pitch speed deg/s (-540 to 540)
            yaw_speed: Yaw speed deg/s (-540 to 540)
        """
        return self._send(f"chassis speed p {pitch_speed} y {yaw_speed}")

    def get_gimbal_attitude(self) -> str:
        """Get gimbal attitude."""
        return self._send("gimbal attitude ?")

    def gimbal_recenter(self) -> str:
        """Recenter the gimbal."""
        return self.gimbal_moveto(0, 0)

    # ========== Blaster ==========

    def blaster_fire(self, times: int = 1) -> str:
        """Fire the blaster."""
        return self._send(f"blaster fire {times}")

    def blaster_led(self, r: int, g: int, b: int, effect: str = "on") -> str:
        """
        Set blaster LED color.

        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)
            effect: 'on', 'off', or 'breathing'
        """
        return self._send(
            f"led control comp bottom_all r {r} g {g} b {b} effect {effect}"
        )

    # ========== LEDs ==========

    def led_gimbal(self, r: int, g: int, b: int, effect: str = "on") -> str:
        """Set gimbal LED color."""
        return self._send(f"led control comp top_all r {r} g {g} b {b} effect {effect}")

    def led_chassis(self, r: int, g: int, b: int, effect: str = "on") -> str:
        """Set chassis LED color."""
        return self._send(
            f"led control comp bottom_all r {r} g {g} b {b} effect {effect}"
        )

    # ========== Armor/Hits ==========

    def armor_event(self, enable: bool = True) -> str:
        """Enable/disable armor hit detection."""
        return self._send(f"armor event {('on' if enable else 'off')}")

    # ========== Camera/Vision ==========

    def camera_exposure(self, value: str = "auto") -> str:
        """Set camera exposure ('auto' or numeric value)."""
        return self._send(f"camera exposure {value}")

    def camera_white_balance(self, value: str = "auto") -> str:
        """Set white balance ('auto', 'locking', or temperature)."""
        return self._send(f"camera wb {value}")

    # ========== Safety ==========

    def quit(self) -> str:
        """Quit SDK mode."""
        return self._send("quit")


def demo():
    """Demo the simple SDK."""
    print("=" * 60)
    print("🤖 Simple SDK Demo")
    print("=" * 60)
    print()

    robot = SimpleRobot()

    if not robot.connect():
        print("Failed to connect!")
        return 1

    try:
        print()
        print("📋 Robot Info:")
        print(f"   Mode: {robot.get_mode()}")
        print(f"   Chassis: {robot.get_chassis_status()}")
        print(f"   Gimbal: {robot.get_gimbal_attitude()}")

        print()
        print("🎮 Demo Movements:")

        # Recenter gimbal
        print("   Recentering gimbal...")
        robot.gimbal_recenter()
        time.sleep(1)

        # Move gimbal
        print("   Moving gimbal...")
        robot.gimbal_moveto(pitch=10, yaw=20)
        time.sleep(1)
        robot.gimbal_recenter()

        # Set LEDs
        print("   Setting LEDs green...")
        robot.led_gimbal(0, 255, 0)
        robot.led_chassis(0, 255, 0)
        time.sleep(0.5)

        print()
        print("✅ Demo complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        robot.close()

    return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        sys.exit(demo())
    else:
        # Interactive mode
        print("=" * 60)
        print("🤖 Simple SDK - Interactive Mode")
        print("=" * 60)
        print()

        robot = SimpleRobot()

        if not robot.connect():
            sys.exit(1)

        print()
        print("Commands: gimbal_recenter(), gimbal_moveto(pitch, yaw)")
        print("          chassis_wheel(w1, w2, w3, w4)")
        print("          led_gimbal(r, g, b), blaster_fire()")
        print("          get_version(), get_gimbal_attitude()")
        print("Type 'quit' to exit")
        print()

        try:
            while True:
                cmd = input(">>> ").strip()
                if cmd.lower() in ("quit", "exit", "q"):
                    break
                if not cmd:
                    continue

                try:
                    result = eval(f"robot.{cmd}")
                    print(f"   {result}")
                except Exception as e:
                    print(f"   Error: {e}")

        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            robot.close()
