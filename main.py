#! /usr/bin/env python3
import time
import numpy as np
import matplotlib.pyplot as plt

# Constants
moon_g = -1.625  # Acceleration due to gravity on the moon.
main_engine_thrust = 45000  # Thrust of main engine in newtons.
sub_engine_thrust = 10000  # Thrust of sub engines in newtons.
engine_min_throttle = 0.2  # Level down to which the engine can throttle (0-1)
specific_impulse = 3000  # Ns/kg. Engine efficiency.


class LanderClass:
    def __init__(self):
        self.fuel = 10000.0                     # mass of fuel in kg
        self.mass = 1000.0                      # Mass of lander in kg
        self.x = 0.0                            # x position in metres
        self.vx = 0.0                           # x velocity in metres per second
        self.ax = 0.0                           # x acceleration in ms^-2
        self.Fx = 0.0                           # x component of force in newtons
        self.y = 0.0                            # y position in metres
        self.vy = 0.0                           # y velocity in metres per second
        self.ay = 0.0                           # y acceleration in ms^-2
        self.Fy = 0.0                           # y component of force in newtons
        # height above the moon's surface.
        self.z = 100.0
        self.vz = 0.0                           # z velocity in metres per second
        self.az = 0.0                           # z acceleration in ms^-2
        self.Fz = 0.0                           # Thrust of engine.
        self.last_tick = time.monotonic()       # Time of last physics update.
        # portion of maximum for x engine's thrust.
        self.thruster_throttle_x = 0.0
        # portion of maximum for y engine's thrust.
        self.thruster_throttle_y = 0.0
        # portion of maximum for z engine's thrust.
        self.thruster_throttle_z = 0.0

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
        global main_engine_thrust
        global sub_engine_thrust
        global specific_impulse
        # Calculate thrusts. Unrealistic as it assumes that the nozzle velocity is the same for both main and sub engines.
        if self.fuel > 0.0:
            self.Fz = main_engine_thrust * self.thruster_throttle_z  # Main engine.
            self.Fx = sub_engine_thrust * self.thruster_throttle_x
            self.Fy = sub_engine_thrust * self.thruster_throttle_y
            # Fuel consumption. For each newton second of thrust use fuel.
            self.fuel -= (self.Fz + self.Fx + self.Fy) * dt / specific_impulse
        else:
            # If there is no fuel the thrust is 0.
            self.Fx, self.Fy, self.Fz = 0.0, 0.0, 0.0
        # Movement from SUVAT equations.
        # x axis movement.
        ax = self.Fx / self.total_mass()
        self.vx += ax * dt
        self.x += self.vx * dt
        # y axis movement.
        ay = self.Fy / self.total_mass()
        self.vz += ay * dt
        self.z += self.vz * dt
        # z axis movement.
        az = self.Fz / self.total_mass() + moon_g
        self.vz += az * dt
        self.z += self.vz * dt
        print(self.z, self.vz, az, dt, self.fuel)


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
    while time_elapsed < 8.0:
        time_elapsed = time.monotonic() - starttime
        lander.physics_tick()
        times.append(time_elapsed)
        heights.append(lander.z)

    # Plot graph of what happended. For development.
    line1, = ax.plot(times, heights, "r")
    plt.show()


if __name__ == "__main__":
    game_loop()
    exit(0)
