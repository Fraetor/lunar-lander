#! /usr/bin/env python3
import time
import numpy as np
import matplotlib.pyplot as plt
import pygame
from pygame.constants import QUIT, K_z

# Constants
moon_g: float = -1.625                                 # Acceleration due to gravity on the moon.
main_engine_thrust: float = 45000.0                    # Thrust of main engine in newtons.
sub_engine_thrust: float = 45000.0                     # Thrust of sub engines in newtons.
engine_min_throttle: float = 0.2                       # Level down to which the engine can throttle (0-1)
specific_impulse: float = 3000.0                       # Ns/kg. Engine efficiency.
throttle_rate: float = 0.2                             # Rate of throttle changing in full throttles per second.
starting_height: float = 100.0                         # Height above the surface that the lander starts.
safe_landing_velocity: float = 3.0                     # Save landing velocity in m/s.
class LanderClass:
    def __init__(self):
        self.fuel: float = 10000.0                     # mass of fuel in kg
        self.mass: float = 1000.0                      # Mass of lander in kg
        self.x: float = 2500.0                         # x position in metres
        self.vx: float = 0.0                           # x velocity in metres per second
        self.ax: float = 0.0                           # x acceleration in ms^-2
        self.Fx: float = 0.0                           # x component of force in newtons
        self.y: float = 2500.0                         # y position in metres
        self.vy: float = 0.0                           # y velocity in metres per second
        self.ay: float = 0.0                           # y acceleration in ms^-2
        self.Fy: float = 0.0                           # y component of force in newtons
        self.z: float = starting_height                # height above the moon's surface.
        self.vz: float = 0.0                           # z velocity in metres per second
        self.az: float = 0.0                           # z acceleration in ms^-2
        self.Fz: float = 0.0                           # Thrust of engine.
        self.last_tick = time.monotonic()              # Time of last physics update.
        self.thruster_throttle_x: float = 0.0          # portion of maximum for x engine's thrust.
        self.thruster_throttle_y: float = 0.0          # portion of maximum for y engine's thrust.
        self.thruster_throttle_z: float = 0.0          # portion of maximum for z engine's thrust.
    
    def throttle_up(self):
        now = time.monotonic()
        dt = now - self.last_tick
        self.thruster_throttle_z += dt * throttle_rate
        # Check that the throttle is set to a reasonable amount.
        if self.thruster_throttle_z >= 1:
            self.thruster_throttle_z = 1.0
        elif self.thruster_throttle_z <= engine_min_throttle:
            self.thruster_throttle_z = engine_min_throttle
    
    def throttle_down(self):
        now = time.monotonic()
        dt = now - self.last_tick
        self.thruster_throttle_z -= dt * throttle_rate
        if self.thruster_throttle_z <= engine_min_throttle:
            self.thruster_throttle_z = 0.0

        
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
    
    def bounds_check(self):
        """
        Ensures the lander doesn't leave the background area and crash the program.
        """
        # Ensures the lander doesn't go too high.
        if self.z > starting_height:
            self.z = starting_height
            # Ensures you actually come back down, rather than being stuck at the top.
            if self.vz > 2.0:
                self.vz = 1.0
        # Ensures the lander doesn't go too far to the sides.
        if self.x > 4950:
            self.x = 4950
        elif self.x < 50:
            self.x = 50
        # Ensures the lander doesn't go too far to the top or bottom.
        if self.y > 4950:
            self.y = 4950
        elif self.y < 50:
            self.y = 50
    
    def zoom_moon(self, moon_surface, screen_size):
        """
        Function to zoom the background surface to the correct level.
        """
        # Prevents the view section from going negative.
        if self.z >= 1:
            subsection_size = self.z / starting_height * moon_surface.get_width()
        else:
            subsection_size = 1 / starting_height * moon_surface.get_width()
        subsection_pos = (self.x - subsection_size/2, self.y - subsection_size/2)
        subsection_rect = pygame.Rect(subsection_pos, (subsection_size, subsection_size)).clip(moon_surface.get_rect())
        #print(subsection_rect)
        moon_subsurface = moon_surface.subsurface(subsection_rect)
        scaled_background = pygame.transform.scale(moon_subsurface, screen_size)
        return scaled_background


def main():
    # Setting up things.
    lander = LanderClass()
    starttime = time.monotonic()
    time_elapsed = 0.0
    
    # Used for plotting the graphs at the end.
    times, heights, velocities = [], [], []

    # Initialise PyGame and create window.
    pygame.init()

    # Size of the window.
    screen_size = (800, 800)
    
    # Sets icon and name of the game window.
    icon = pygame.image.load("graphics/icon.png")
    icon.set_colorkey(pygame.Color(255, 0, 255))
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Lunar Lander")
    screen = pygame.display.set_mode(screen_size)
    moon_surface = pygame.image.load("graphics/moon.png").convert()
    background = pygame.Surface(screen_size)
    screen.blit(background, (0, 0))


    def render():
        """
        Updates the screen with the current situation.
        """
        background = lander.zoom_moon(moon_surface, screen_size)
        screen.blit(background, (0, 0))
        pygame.display.flip()
    

    def check_keys():
        """
        Checks to see if any keys are pressed and causes their effects.
        """
        keys = pygame.key.get_pressed()
        # main thruster controls.
        if keys[pygame.K_SPACE]:
            lander.throttle_up()
        elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            lander.throttle_down()
        # Maximum/zero thrust shortcuts.
        if keys[pygame.K_x]:
            lander.thruster_throttle_z = 1.0
        elif keys[pygame.K_z]:
            lander.thruster_throttle_z = 0.0
        # x axis subthrusters (left/right)
        if keys[pygame.K_RIGHT]:
            lander.thruster_throttle_x = 1.0
        elif keys[pygame.K_LEFT]:
            lander.thruster_throttle_x = -1.0
        else:
            lander.thruster_throttle_x = 0.0
        # y axis subthrusters (up/down)
        if keys[pygame.K_UP]:
            lander.thruster_throttle_y = -1.0
        elif keys[pygame.K_DOWN]:
            lander.thruster_throttle_y = 1.0
        else:
            lander.thruster_throttle_y = 0.0
        # Exit the game.
        if keys[pygame.K_ESCAPE]:
            quit()
    

    def readouts():
        print(f"Height: {lander.z:.2f}m Velocity: {lander.total_velocity():.2f}m/s Thrust: {lander.Fz:.2f}N Fuel: {lander.fuel:.2f}kg")

    
    def events():
        """
        Handles the pygame event queue.
        """
        for event in pygame.event.get():
            # Makes the window close button work.
            if event.type == pygame.QUIT:
                quit()
    

    def gen_summary_graphs():
        # Plot graph of what happended. For display at the end.
        # Create graph to display descent.
        fig = plt.figure("lander_graph")
        ax = fig.add_subplot()
        ax.plot(times, heights, "r")
        #plt.savefig("height.png")
    

    def startup_screen():
        # A screen with instructions and such that is displayed before the game starts.
        pass # Not yet implimented.


    def ending_screen():
        print(f"Landed at {lander.total_velocity():.2f} m/s after {time_elapsed:.2f} seconds.")
        if lander.total_velocity() <= safe_landing_velocity:
            print("The landing was successful.")
        else:
            print("You crashed!\nKABOOM!")
        # Generate summary graphs of the flight.
        gen_summary_graphs()
        # Display an ending screen with the graphs embedded.
        pass # Not yet implimented.


    startup_screen()

    # Main game loop
    while True:
        time_elapsed = time.monotonic() - starttime

        times.append(time_elapsed)
        heights.append(lander.z)
        velocities.append(lander.total_velocity())

        check_keys()
        lander.physics_tick()
        lander.bounds_check()
        readouts()
        render()
        events()

        # Break out of loop once we have landed/hit the ground.
        if lander.z <= 0.0:
            break
    
    ending_screen()





if __name__ == "__main__":
    main()
    exit(0)
