import pygame
import pydicom
from OpenGL.GL import *
from pygame.locals import *
import numpy as np


def init_window(width, height):
   pygame.init()
   screen = pygame.display.set_mode((2 * width, 2 * height), DOUBLEBUF | OPENGL)
   pygame.display.set_caption("Перегляд DICOM")
   glClearColor(0.0, 0.0, 0.0, 1.0)
   glMatrixMode(GL_PROJECTION)
   glLoadIdentity()
   glOrtho(-width, width, -height, height, -1, 1)


def load_dicom_image(file_path):
   dicom_data = pydicom.dcmread(file_path)
   image_data = dicom_data.pixel_array
   image_data = np.interp(image_data, (image_data.min(), image_data.max()), (0, 255)).astype(np.uint8)
   image_data = np.rot90(image_data, k=1)
   pixel_spacing = dicom_data.PixelSpacing if "PixelSpacing" in dicom_data else (1.0, 1.0)
   image_position = dicom_data.ImagePositionPatient if "ImagePositionPatient" in dicom_data else (0.0, 0.0, 0.0)
   return dicom_data, image_data, pixel_spacing, image_position


def display_image(image_data, width, height):
   glRasterPos2i(-width, height - image_data.shape[0])
   image_data = np.flipud(image_data)
   glDrawPixels(width, height, GL_LUMINANCE, GL_UNSIGNED_BYTE, image_data)


def create_text_texture(text, font_size=14):
   font = pygame.font.SysFont('Arial', font_size)
   text_surface = font.render(text, True, (255, 255, 255), (0, 0, 0))
   text_data = pygame.image.tostring(text_surface, "RGBA", True)
   text_width, text_height = text_surface.get_size()
   texture_id = glGenTextures(1)
   glBindTexture(GL_TEXTURE_2D, texture_id)
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
   glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_width, text_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
   return texture_id, text_width, text_height


def render_text_flipped_vertical(texture_id, text_width, text_height, x, y):
   glEnable(GL_TEXTURE_2D)
   glBindTexture(GL_TEXTURE_2D, texture_id)
   glColor3f(1, 1, 1)
   glBegin(GL_QUADS)
   glTexCoord2f(0, 0)
   glVertex2f(x, y)
   glTexCoord2f(1, 0)
   glVertex2f(x + text_width, y)
   glTexCoord2f(1, 1)
   glVertex2f(x + text_width, y + text_height)
   glTexCoord2f(0, 1)
   glVertex2f(x, y + text_height)
   glEnd()
   glDisable(GL_TEXTURE_2D)


def main():
   dicom_file_path = '_DICOM_Image_for_Lab_2.dcm'
   dicom_data, image_data, pixel_spacing, image_position = load_dicom_image(dicom_file_path)
   image_height, image_width = image_data.shape
   init_window(image_width, image_height)
   show_image = False
   running = True


   while running:
       glClear(GL_COLOR_BUFFER_BIT)
       if show_image:
           display_image(image_data, image_width, image_height)


       text_A_id, text_A_width, text_A_height = create_text_texture("A")
       render_text_flipped_vertical(
           text_A_id, text_A_width, text_A_height,
           -image_width + 10, 0 - text_A_height // 2
       )


       text_L_id, text_L_width, text_L_height = create_text_texture("L")
       render_text_flipped_vertical(
           text_L_id, text_L_width, text_L_height,
           -text_L_width // 2, -image_height + 10
       )


       for event in pygame.event.get():
           if event.type == QUIT:
               running = False
           elif event.type == KEYDOWN:
               if event.key == K_SPACE:
                   show_image = not show_image


       mouse_x, mouse_y = pygame.mouse.get_pos()
       screen_x = mouse_x - image_width
       screen_y = image_height - mouse_y
       coords_text = f"Screen: ({screen_x}, {screen_y})"


       if show_image:
           dicom_x = screen_x * pixel_spacing[0] + image_position[0]
           dicom_y = screen_y * pixel_spacing[1] + image_position[1]
           dicom_z = image_position[2]
           coords_text += f" | DICOM: ({dicom_x:.2f}, {dicom_y:.2f}, {dicom_z:.2f})"


       coords_texture_id, coords_width, coords_height = create_text_texture(coords_text)
       render_text_flipped_vertical(coords_texture_id, coords_width, coords_height, -coords_width // 2, -image_height + 20)
       pygame.display.flip()


   pygame.quit()


if __name__ == "__main__":
   main()
