
from object_3d import *
from camera import *
from projection import *
import pygame as pg
import math

class SoftwareRender:
    def __init__(self):
        # Initialize Pygame
        pg.init()
        
        # Screen settings
        self.RES = self.WIDTH, self.HEIGHT = 1000, 500
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        
        # Frames per second
        self.FPS = 60
        
        # Pygame screen and clock setup
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        
        # Create 3D objects and set up initial state
        self.create_objects()

    def create_objects(self):
        # Create camera, projection, and 3D object
        self.camera = Camera(self, [-5, 6, -55])
        self.projection = Projection(self)
        self.object = self.get_object_from_file('t_34_obj.obj')
        
        # Rotate the object for initial orientation
        self.object.rotate_y(-math.pi / 4)

    def get_object_from_file(self, filename):
        # Load 3D object from an OBJ file
        vertex, faces = [], []
        with open(filename) as f:
            for line in f:
                if line.startswith('v '):
                    # Parse vertices
                    vertex.append([float(i) for i in line.split()[1:]] + [1])
                elif line.startswith('f'):
                    # Parse faces
                    faces_ = line.split()[1:]
                    faces.append([int(face_.split('/')[0]) - 1 for face_ in faces_])
        return Object3D(self, vertex, faces)

    def draw(self):
        # Draw the 3D scene on the Pygame screen
        self.screen.fill(pg.Color('darkslategray'))
        self.object.draw()

    def run(self):
        # Main application loop
        while True:
            self.draw()
            
            # Handle user input for camera control
            self.camera.control()
            
            # Check for quit event
            [exit() for i in pg.event.get() if i.type == pg.QUIT]
            
            # Update Pygame display caption with current frames per second
            pg.display.set_caption(str(self.clock.get_fps()))
            
            # Update the display
            pg.display.flip()
            
            # Cap the frame rate
            self.clock.tick(self.FPS)

# Entry point for the application
if __name__ == '__main__':
    app = SoftwareRender()
    app.run()
