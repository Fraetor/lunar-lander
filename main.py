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
        """
        Returns the total mass of the lander, including consumables.
        """
        return self.mass + self.fuel

    def total_velocity(self):
        """
        Returns the total velocity of the lander, taking into account all components.
        """
        return np.sqrt(np.square(self.vx) + np.square(self.vy) + np.square(self.vz))

    def physics_tick(self):
        """
        Computes the dynamics changes since the last tick.
        """
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
    
    def zoom_moon(self, moon_surface, screen_size):
        """
        Function to zoom the background surface to the correct level.
        """
        # Prevents the view section from going negative.
        if self.z >= 1:
            subsection_size = self.z / 100 * moon_surface.get_width()
        else:
            subsection_size = 1 / 100 * moon_surface.get_width()
        subsection_pos = (self.x, self.y)
        subsection_rect = pygame.Rect(subsection_pos, (subsection_size, subsection_size))
        print(subsection_rect)
        moon_subsurface = moon_surface.subsurface(subsection_rect)
        scaled_background = pygame.transform.scale(moon_subsurface, screen_size)
        return scaled_background


def main():
    # Setting up things.
    lander = LanderClass()
    starttime = time.monotonic()
    time_elapsed = 0.0
    
    # Used for plotting the graphs at the end.
    times, heights = [], []

    # Initialise PyGame and create window.
    pygame.init()
    screen_size = (800, 800)
    # pygame.display.set_icon(Surface)
    pygame.display.set_caption("Lunar Lander")
    screen = pygame.display.set_mode(screen_size)
    moon_surface = pygame.image.load("moon.png").convert()
    background = pygame.Surface(screen_size)
    screen.blit(background, (0, 0))

    def render():
        background = lander.zoom_moon(moon_surface, screen_size)
        screen.blit(background, (0, 0))
        pygame.display.flip()
        pygame.time.wait(500)
    
    # Main game loop
    while True:
        time_elapsed = time.monotonic() - starttime
        lander.physics_tick()

        times.append(time_elapsed)
        heights.append(lander.z)
        
        render()
        for event in pygame.event.get():
            # Makes the close button work.
            if event.type == pygame.QUIT:
                quit()

        if lander.z <= 0.0:
            print(f"Landed at {lander.total_velocity():.2f} m/s after {time_elapsed:.2f} seconds.")
            if lander.total_velocity() <= 1:
                print("The landing was successful.")
            else:
                print("You crashed!\nKABOOM!")
            # Plot graph of what happended. For display at the end.
            # Create graph to display descent.
            fig = plt.figure("lander_graph")
            ax = fig.add_subplot()
            ax.plot(times, heights, "r")
            plt.savefig("testplot.pdf")
            break


if __name__ == "__main__":
    main()
    exit(0)
