#! /usr/bin/env python3
import time
import numpy as np
import matplotlib.pyplot as plt
import pygame

# Constants
moon_g: float = -1.625                                 # Acceleration due to gravity on the moon.
main_engine_thrust: float = 45000.0                    # Thrust of main engine in newtons.
sub_engine_thrust: float = 45000.0                     # Thrust of sub engines in newtons.
specific_impulse: float = 3000.0                       # Ns/kg. Engine efficiency.
throttle_rate: float = 0.2                             # Rate of throttle changing in full throttles per second.
starting_height: float = 1000.0                        # Height above the surface that the lander starts.
safe_landing_velocity: float = 3.0                     # Save landing velocity in m/s.
target = {"x": 3400, "y": 2700}                        # Landing target. Image coordinates on the background image.




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
        """
        Steadily throttles up the main engine.
        """
        now = time.monotonic()
        dt = now - self.last_tick
        self.thruster_throttle_z += dt * throttle_rate
        # Check that the throttle is set to a reasonable amount.
        if self.thruster_throttle_z >= 1:
            self.thruster_throttle_z = 1.0
    

    def throttle_down(self):
        """
        Steadily throttles up the main engine.
        """
        now = time.monotonic()
        dt = now - self.last_tick
        self.thruster_throttle_z -= dt * throttle_rate
        if self.thruster_throttle_z <= 0:
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
        Function to zoom and crop the background surface to the correct level for display.
        """
        # Prevents the view section from going negative.
        if self.z >= 1:
            subsection_size = self.z / starting_height * moon_surface.get_width()
        else:
            subsection_size = 1 / starting_height * moon_surface.get_width()
        
        subsection_pos = (self.x - subsection_size/2, self.y - subsection_size/2)
        subsection_rect = pygame.Rect(subsection_pos, (subsection_size, subsection_size)).clip(moon_surface.get_rect())
        moon_subsurface = moon_surface.subsurface(subsection_rect)
        scaled_background = pygame.transform.scale(moon_subsurface, screen_size)
        return scaled_background




def main():
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
        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            quit()
    

    def readouts():
        """
        Prepares readout surfaces for bliting to the screen during the render.
        """
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
        fig = plt.figure("lander_graph", figsize=(8,6))
        ax = fig.add_subplot()
        ax.plot(times, heights, "r")
        plt.xlabel("Time / s")
        plt.ylabel("Height / m")
        plt.savefig("__heightgraph.png", dpi=50)
    

    def startup_screen():
        """
        Displays a screen with instructions and such that is displayed before the game starts.
        """
        startscreen = pygame.image.load("graphics/startscreen.png").convert()
        pygame.transform.smoothscale(startscreen, screen_size, background)
        screen.blit(background, (0, 0))
        pygame.display.flip()
        # Wait for the space bar to be pressed before continuing.
        while True:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:  # Press space to start.
                break
            elif keys[pygame.K_ESCAPE] or keys[pygame.K_q]:  # Press escape or 'q' to quit.
                quit()
            # Handle events while on startup screen.
            events()
            # Stops this using loads of CPU time.
            pygame.time.wait(10)


    def ending_screen():
        """
        Displays a screen after landing or crashing, displaying flight statistics, and giving the option to restart or quit.
        """
        # Calculate distance from target in centre of clearing.
        distance_from_target = np.sqrt(np.square(lander.x - target["x"]) + np.square(lander.y - target["y"]))
        print(f"Landed at {lander.total_velocity():.2f} m/s after {time_elapsed:.2f} seconds, {distance_from_target:.2f}m away from the target.")
        bigText = pygame.font.Font(None, 120)
        smallText = pygame.font.Font(None, 40)
        if lander.total_velocity() <= safe_landing_velocity:
            print("The landing was successful.")
            end_status = bigText.render("LANDED!", True, (255, 255, 255))
        else:
            print("You crashed!\nKABOOM!")
            end_status = bigText.render("CRASHED!", True, (255, 255, 255))
        # Generate summary graphs of the flight.
        gen_summary_graphs()
        # Display an ending screen with the graphs embedded.
        endscreen = pygame.image.load("graphics/endscreen.png").convert()
        # Here is where we need to blit the graphs onto the endscreen.
        height_graph = pygame.image.load("__heightgraph.png").convert()
        # Renders summary text to the screen.
        end_speed = smallText.render(f"{lander.total_velocity():.2f}", True, (255, 255, 255))
        end_time = smallText.render(f"{time_elapsed:.2f}", True, (255, 255, 255))
        end_distance = smallText.render(f"{distance_from_target:.2f}", True, (255, 255, 255))
        endscreen.blit(end_status, pygame.Rect((176, 30), (464, 160)))
        endscreen.blit(end_speed, pygame.Rect((221, 218), (92, 40)))
        endscreen.blit(end_time, pygame.Rect((268, 294), (92, 40)))
        endscreen.blit(end_distance, pygame.Rect((178, 369), (92, 40)))
        endscreen.blit(height_graph, pygame.Rect((200, 440), (92, 40)))
        pygame.transform.smoothscale(endscreen, screen_size, background)
        screen.blit(background, (0, 0))
        pygame.display.flip()
        # Wait for user input to be pressed before continuing.
        while True:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q] or keys[pygame.K_ESCAPE]:  # Press 'q' to exit.
                break
            elif keys[pygame.K_r]:  # Press 'r' to restart.
                main()
            # Handle events while on end screen.
            events()
            # Stops this using loads of CPU time.
            pygame.time.wait(10)


    startup_screen()

    # Setting up physics state.
    lander = LanderClass()
    time_elapsed = 0.0
    starttime = time.monotonic()
    
    # Used for plotting the graphs at the end.
    times, heights, velocities = [], [], []

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




# Doesn't run program if it is imported as a module.
if __name__ == "__main__":
    main()
    exit(0)
