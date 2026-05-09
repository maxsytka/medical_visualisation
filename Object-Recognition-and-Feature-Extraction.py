import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


class DicomPixelLocator:
   def __init__(self):
       self.rows = 512
       self.columns = 512
       self.pixel_spacing = [0.703125, 0.703125]
       self.slice_thickness = 2.50
       self.spacing_between_slices = 2.50


       self.first_slice_position = np.array([-161.4, -180.0, -161.25])
       self.target_slice_position = np.array([-161.4, -180.0, -461.25])
       self.orientation_matrix = np.array([
           [1.0, 0.0, 0.0],
           [0.0, 1.0, 0.0],
           [0.0, 0.0, 1.0]
       ])


       self.total_slices = 126
       self.target_pixel = [168, 138]


       pygame.init()
       self.width, self.height = 800, 600
       pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.OPENGL)
       pygame.display.set_caption("DICOM Pixel Locator")
       gluPerspective(45, (self.width / self.height), 0.1, 1000.0)
       glTranslatef(0.0, 0.0, -500)


       glClearColor(0.1, 0.1, 0.1, 1)


   def calculate_pixel_coordinates(self, row, col):
       if row < 0 or row >= self.rows or col < 0 or col >= self.columns:
           raise ValueError("Некоректні координати пікселя")


       pixel_x = col * self.pixel_spacing[0]
       pixel_y = row * self.pixel_spacing[1]
       pixel_3d = self.target_slice_position + np.dot(self.orientation_matrix, [pixel_x, pixel_y, 0])


       return pixel_3d


   def draw_axes(self):
       glBegin(GL_LINES)
       glColor3f(1, 0, 0)  # X-axis
       glVertex3f(0, 0, 0)
       glVertex3f(100, 0, 0)


       glColor3f(0, 1, 0)  # Y-axis
       glVertex3f(0, 0, 0)
       glVertex3f(0, 100, 0)


       glColor3f(0, 0, 1)  # Z-axis
       glVertex3f(0, 0, 0)
       glVertex3f(0, 0, 100)
       glEnd()


   def draw_pixel(self, pixel_coord):
       glPointSize(10)
       glColor3f(1, 0, 0)
       glBegin(GL_POINTS)
       glVertex3f(*pixel_coord)
       glEnd()


   def draw_volume(self):
       glColor3f(0.5, 0.5, 0.5)
       glBegin(GL_LINE_LOOP)
       volume_min = self.first_slice_position
       volume_max = self.first_slice_position + [
           (self.columns - 1) * self.pixel_spacing[0],
           (self.rows - 1) * self.pixel_spacing[1],
           (self.total_slices - 1) * self.spacing_between_slices
       ]
       for corner in [
           volume_min,
           [volume_max[0], volume_min[1], volume_min[2]],
           [volume_max[0], volume_max[1], volume_min[2]],
           [volume_min[0], volume_max[1], volume_min[2]],
           volume_min
       ]:
           glVertex3f(*corner)
       glEnd()


   def run(self):
       running = True
       rotation_x, rotation_y = 0, 0
       while running:
           for event in pygame.event.get():
               if event.type == pygame.QUIT:
                   running = False


           keys = pygame.key.get_pressed()
           if keys[pygame.K_LEFT]:
               rotation_y -= 2
           if keys[pygame.K_RIGHT]:
               rotation_y += 2
           if keys[pygame.K_UP]:
               rotation_x -= 2
           if keys[pygame.K_DOWN]:
               rotation_x += 2


           glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
           glPushMatrix()
           glRotatef(rotation_x, 1, 0, 0)
           glRotatef(rotation_y, 0, 1, 0)


           self.draw_axes()
           self.draw_volume()


           pixel_3d = self.calculate_pixel_coordinates(*self.target_pixel)
           self.draw_pixel(pixel_3d)


           glPopMatrix()
           pygame.display.flip()
           pygame.time.wait(10)


       pygame.quit()


if __name__ == "__main__":
   app = DicomPixelLocator()
   app.run()
