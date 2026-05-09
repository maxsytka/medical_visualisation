import pygame
import pydicom
from OpenGL.GL import *
from pygame.locals import *
import numpy as np




def init_window(width, height):
   pygame.init()
   screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
   pygame.display.set_caption("Перегляд DICOM зображення з можливістю відображення тексту")
   glClearColor(0.0, 0.0, 0.0, 1.0)
   glMatrixMode(GL_PROJECTION)
   glLoadIdentity()
   glOrtho(0, width, height, 0, -1, 1)




def load_dicom_image(file_path):
   dicom_data = pydicom.dcmread(file_path)


   width = int(dicom_data.Rows)
   height = int(dicom_data.Columns)


   dtype = np.dtype(f'int{dicom_data.BitsAllocated}')


   image_data = dicom_data.pixel_array.astype(dtype)
   image_data = np.flipud(image_data)


   return dicom_data, image_data, width, height




def display_image(image_data, width, height):
   glDrawPixels(width, height, GL_LUMINANCE, GL_UNSIGNED_BYTE, image_data)




def create_text_texture(text, font_size=24):
   font = pygame.font.SysFont('Arial', font_size)
   text_surface = font.render(text, True, (255, 255, 255), (0, 0, 0))  # Білий текст на чорному фоні
   text_data = pygame.image.tostring(text_surface, "RGBA", True)
   text_width, text_height = text_surface.get_size()


   luminance_alpha_data = []
   for i in range(0, len(text_data), 4):
       r, g, b, a = text_data[i:i+4]
       luminance = int(0.299 * r + 0.587 * g + 0.114 * b)
       luminance_alpha_data.extend([luminance, a])


   luminance_alpha_data = bytes(luminance_alpha_data)


   texture_id = glGenTextures(1)
   glBindTexture(GL_TEXTURE_2D, texture_id)
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
   glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE_ALPHA, text_width, text_height, 0, GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE, luminance_alpha_data)


   return texture_id, text_width, text_height






def render_text(texture_id, text_width, text_height, x, y):
   glEnable(GL_TEXTURE_2D)
   glBindTexture(GL_TEXTURE_2D, texture_id)


   glColor3f(1, 1, 1)
   glBegin(GL_QUADS)


   glTexCoord2f(0, 1)  # Нижній лівий кут
   glVertex2f(x, y)
   glTexCoord2f(1, 1)  # Нижній правий кут
   glVertex2f(x + text_width, y)
   glTexCoord2f(1, 0)  # Верхній правий кут
   glVertex2f(x + text_width, y + text_height)
   glTexCoord2f(0, 0)  # Верхній лівий кут
   glVertex2f(x, y + text_height)


   glEnd()


   glDisable(GL_TEXTURE_2D)




def main():
   dicom_file_path = '_DICOM_Image_for_Lab_2.dcm'
   dicom_data, image_data, image_width, image_height = load_dicom_image(dicom_file_path)


   init_window(image_width, image_height)


   conversion_type = dicom_data.get("ConversionType", "Тип перетворення відсутній")
   text_texture_id, text_width, text_height = create_text_texture(f"Тип перетворення: {conversion_type}")


   running = True
   show_text = False
   while running:
       for event in pygame.event.get():
           if event.type == QUIT:
               running = False
           elif event.type == MOUSEBUTTONDOWN:
               if event.button == 1:
                   show_text = not show_text


       glClear(GL_COLOR_BUFFER_BIT)


       display_image(image_data, image_width, image_height)


       if show_text:
           render_text(text_texture_id, text_width, text_height, 10, image_height - text_height - 10)


       pygame.display.flip()


   pygame.quit()




if __name__ == "__main__":
   main()
