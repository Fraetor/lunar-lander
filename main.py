#! /usr/bin/env python3
import time


# Constants
moon_g = -1.625  # Acceleration due to gravity on the moon.


class Lander:
    def __init__(self):
        self.fuel = 100.0  # kg of fuel
        self.mass = 1000.0  # Mass of lander in kg
        self.x = 0.0  # x position in metres
        self.vx = 0.0
        self.y = 0.0  # y position in metres
        self.vx = 0.0
        self.z = 100.0  # height above the moon.
        self.vz = 0.0
        self.Fz = 0.0  # Thrust of engine.

    def total_mass(self):
        return self.mass + self.fuel


ticktime = time.monotonic


def time_since_last_tick():
    global ticktime
    old_now = ticktime
    ticktime = time.monotonic
    tick_length = old_now = ticktime
    return tick_length


def physics_tick():
    dt = time_since_last_tick()
    global moon_g

    az = lander.Fz / lander.total_mass() + moon_g
    lander.vz = lander.vz + az * dt
    lander.z = lander.z + lander.vz * dt


lander = Lander


if __name__ == "__main__":
    # Do main stuff.
    pass
