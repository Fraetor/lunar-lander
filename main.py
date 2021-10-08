#! /usr/bin/env python3
import time
import numpy as np
import matplotlib.pyplot as plt

# Constants
moon_g = -1.625  # Acceleration due to gravity on the moon.


class LanderClass:
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
        self.last_tick = time.monotonic()

    def total_mass(self):
        return self.mass + self.fuel

    def total_velocity(self):
        return np.sqrt(np.square(self.vx) + np.square(self.vy) + np.square(self.vz))

    def physics_tick(self):
        # Calculate dt
        now = time.monotonic()
        dt = now - self.last_tick
        self.last_tick = now
        # Allow access to global constants.
        global moon_g
        # SUVAT equations:
        az = self.Fz / self.total_mass() + moon_g
        self.vz = self.vz + az * dt
        self.z = self.z + self.vz * dt
        print(self.z, self.vz, az, dt)


def game_loop():
    # Setting up things.
    lander = LanderClass()
    starttime = time.monotonic()
    time_elapsed = 0.0

    # Create graph to display descent.
    fig = plt.figure("lander_graph")
    ax = fig.add_subplot()
    times, heights = [], []

    # Main game loop
    while time_elapsed < 5:
        time_elapsed = time.monotonic() - starttime
        lander.physics_tick()
        times.append(time_elapsed)
        heights.append(lander.z)

    # Plot graph of what happended. For development.
    line1, = ax.plot(times, heights, "r")
    plt.show()

if __name__ == "__main__":
    game_loop()
    exit(1)
