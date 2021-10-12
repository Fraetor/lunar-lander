#! /usr/bin/env python3
import time
import numpy as np
import matplotlib.pyplot as plt
import pygame

# Constants
moon_g: float = -1.625                                 # Acceleration due to gravity on the moon.
main_engine_thrust: float = 45000.0                    # Thrust of main engine in newtons.
sub_engine_thrust: float = 10000.0                     # Thrust of sub engines in newtons.
engine_min_throttle: float = 0.2                       # Level down to which the engine can throttle (0-1)
specific_impulse: float = 3000.0                       # Ns/kg. Engine efficiency.


class LanderClass:
    def __init__(self):
        self.fuel: float = 10000.0                     # mass of fuel in kg
        self.mass: float = 1000.0                      # Mass of lander in kg
        self.x: float = 0.0                            # x position in metres
        self.vx: float = 0.0                           # x velocity in metres per second
        self.ax: float = 0.0                           # x acceleration in ms^-2
        self.Fx: float = 0.0                           # x component of force in newtons
        self.y: float = 0.0                            # y position in metres
        self.vy: float = 0.0                           # y velocity in metres per second
        self.ay: float = 0.0                           # y acceleration in ms^-2
        self.Fy: float = 0.0                           # y component of force in newtons
        self.z: float = 100.0                          # height above the moon's surface.
        self.vz: float = 0.0                           # z velocity in metres per second
        self.az: float = 0.0                           # z acceleration in ms^-2
        self.Fz: float = 0.0                           # Thrust of engine.
        self.last_tick = time.monotonic()              # Time of last physics update.
        self.thruster_throttle_x: float = 0.0          # portion of maximum for x engine's thrust.
        self.thruster_throttle_y: float = 0.0          # portion of maximum for y engine's thrust.
        self.thruster_throttle_z: float = 0.0          # portion of maximum for z engine's thrust.

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
        self.vy += ay * dt
        self.y += self.vy * dt
        # z axis movement.
        az = self.Fz / self.total_mass() + moon_g
        self.vz += az * dt
        self.z += self.vz * dt
        #print(self.z, self.vz, az, dt, self.fuel)


def game_loop():
    # Setting up things.
    lander = LanderClass()
    starttime = time.monotonic()
    time_elapsed = 0.0

    # Create graph to display descent.
    fig = plt.figure("lander_graph")
    ax = fig.add_subplot()
    times, heights = [], []

    # Initialse PyGame and create window.
    pygame.init()
    screen_width, screen_height = 800, 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    background = pygame.Surface((screen_width, screen_height))
    moon_surface = pygame.image.load("moon.png").convert()
    background.blit(moon_surface, (0, 0))
    pygame.draw.rect(background, pygame.Color(100, 0, 0), pygame.Rect((100, 100, 30, 20)))
    screen.blit(background, (0, 0))
    def render():
        screen.blit(background, (0, 0))



    # Main game loop
    while True:
        time_elapsed = time.monotonic() - starttime
        lander.physics_tick()
        times.append(time_elapsed)
        heights.append(lander.z)
        render()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        if lander.z <= 0.0:
            print(f"Landed at {lander.total_velocity()} m/s after {time_elapsed} seconds.")
            # Plot graph of what happended. For development.
            ax.plot(times, heights, "r")
            plt.savefig("testplot.pdf")
            break


if __name__ == "__main__":
    game_loop()
    exit(0)
