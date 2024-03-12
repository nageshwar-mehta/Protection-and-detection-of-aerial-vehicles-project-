import pygame as pg
from matrix_functions import *
from numba import njit

# Numba decorator for just-in-time compilation to improve performance
@njit(fastmath=True)
def any_func(arr, a, b):
    return np.any((arr == a) | (arr == b))

class Object3D:
    def __init__(self, render, vertices='', faces=''):
        # Initialize the 3D object with vertices, faces, and rendering information
        self.render = render
        self.vertices = np.array(vertices)
        self.faces = faces
        self.translate([0.0001, 0.0001, 0.0001])  # Small initial translation to avoid numerical issues

        # Font for labels
        self.font = pg.font.SysFont('Arial', 30, bold=True)

        # Color each face with a color and store in a list
        self.color_faces = [(pg.Color('white'), face) for face in self.faces]

        # Flags for movement and drawing vertices
        self.movement_flag, self.draw_vertices = True, False
        self.label = ''  # Label for each face

    def draw(self):
        # Main draw method for the 3D object
        self.screen_projection()
        self.movement()

    def movement(self):
        # Update the object's rotation over time for animation
        if self.movement_flag:
            self.rotate_y(-(pg.time.get_ticks() % 0.005))

    def screen_projection(self):
        # Project 3D object vertices onto the 2D screen
        vertices = self.vertices @ self.render.camera.camera_matrix()
        vertices = vertices @ self.render.projection.projection_matrix
        vertices /= vertices[:, -1].reshape(-1, 1)
        vertices[(vertices > 2) | (vertices < -2)] = 0
        vertices = vertices @ self.render.projection.to_screen_matrix
        vertices = vertices[:, :2]

        # Draw each face using Pygame's polygon drawing
        for index, color_face in enumerate(self.color_faces):
            color, face = color_face
            polygon = vertices[face]

            # Check if any vertex is outside the screen boundaries before drawing
            if not any_func(polygon, self.render.H_WIDTH, self.render.H_HEIGHT):
                pg.draw.polygon(self.render.screen, color, polygon, 1)
                
                # Display label at the last vertex of the face
                if self.label:
                    text = self.font.render(self.label[index], True, pg.Color('white'))
                    self.render.screen.blit(text, polygon[-1])

        # Optionally draw individual vertices
        if self.draw_vertices:
            for vertex in vertices:
                if not any_func(vertex, self.render.H_WIDTH, self.render.H_HEIGHT):
                    pg.draw.circle(self.render.screen, pg.Color('white'), vertex, 2)

    def translate(self, pos):
        # Translate the object by a given position vector
        self.vertices = self.vertices @ translate(pos)

    def scale(self, scale_to):
        # Scale the object by a given factor along all axes
        self.vertices = self.vertices @ scale(scale_to)

    def rotate_x(self, angle):
        # Rotate the object around the x-axis by a given angle in radians
        self.vertices = self.vertices @ rotate_x(angle)

    def rotate_y(self, angle):
        # Rotate the object around the y-axis by a given angle in radians
        self.vertices = self.vertices @ rotate_y(angle)

    def rotate_z(self, angle):
        # Rotate the object around the z-axis by a given angle in radians
        self.vertices = self.vertices @ rotate_z(angle)


class Axes(Object3D):
    def __init__(self, render):
        # Initialize Axes object as a subclass of Object3D
        super().__init__(render)

        # Define vertices and faces for the XYZ axes
        self.vertices = np.array([(0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)])
        self.faces = np.array([(0, 1), (0, 2), (0, 3)])

        # Define colors for the axes
        self.colors = [pg.Color('red'), pg.Color('green'), pg.Color('blue')]

        # Color each face with a color and store in a list
        self.color_faces = [(color, face) for color, face in zip(self.colors, self.faces)]

        # Flags for drawing vertices and labels
        self.draw_vertices = False
        self.label = 'XYZ'  # Label for each face
