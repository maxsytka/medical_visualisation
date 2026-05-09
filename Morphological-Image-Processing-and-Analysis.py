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
    image_data = dicom_data.pixel_array
    image_data = np.interp(image_data, (image_data.min(), image_data.max()), (0, 255)).astype(np.uint8)
    return dicom_data, image_data

def save_dicom_image(file_path, dicom_data, image_data):
    dicom_data.PixelData = image_data.tobytes()
    dicom_data.Rows, dicom_data.Columns = image_data.shape
    dicom_data.save_as(file_path)

def display_image(image_data, width, height):
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

def render_text(texture_id, text_width, text_height, x, y):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1)
    glVertex2f(x, y)
    glTexCoord2f(1, 1)
    glVertex2f(x + text_width, y)
    glTexCoord2f(1, 0)
    glVertex2f(x + text_width, y + text_height)
    glTexCoord2f(0, 0)
    glVertex2f(x, y + text_height)
    glEnd()

    glDisable(GL_TEXTURE_2D)

def linear_transformation(image_data, scaling_factor, offset):
    new_image_data = scaling_factor * image_data + offset
    return np.clip(new_image_data, 0, 255).astype(np.uint8)

def change_pixel_range(image_data, lower_limit, upper_limit):
    image_data = np.clip(image_data, lower_limit, upper_limit)
    return image_data

def main():
    dicom_file_path = '_DICOM_Image_for_Lab_2.dcm'
    dicom_data, original_image_data = load_dicom_image(dicom_file_path)
    image_height, image_width = original_image_data.shape

    init_window(image_width, image_height)

    scaling_factor = 0.012953
    offset = 3.724
    lower_limit = 60
    upper_limit = 225

    running = True
    show_text = False
    linear_transform = False
    high_low_borders = False
    current_image_data = original_image_data.copy()

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            min_pixel = current_image_data.min()
            max_pixel = current_image_data.max()
            pixel_type = current_image_data.dtype
            image_type = dicom_data.get((0x0008, 0x0008), "Image Type відсутній")

            info_text = (f"Мін:{min_pixel}, Макс:{max_pixel}, Тип:{pixel_type}, Image Type:{image_type}")
            text_texture_id, text_width, text_height = create_text_texture(info_text)

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    show_text = not show_text
            elif event.type == KEYDOWN:
                if event.key == pygame.K_1:
                    print("Виконано лінійне перетворення.")
                    linear_transform = True
                elif event.key == pygame.K_2:
                    print("Змінено діапазон значень пікселів.")
                    high_low_borders = True
                elif event.key == pygame.K_3:
                    print("Виконано комбінування операцій.")
                    linear_transform = True
                    high_low_borders = True
                elif event.key == pygame.K_4:
                    current_image_data = original_image_data.copy()
                    print("Відновлено оригінальне зображення.")
                    linear_transform = False
                    high_low_borders = False
                elif event.key == pygame.K_5:
                    output_file_path = 'output_image.dcm'
                    save_dicom_image(output_file_path, dicom_data, current_image_data)
                    print(f"Зображення збережено до {output_file_path}.")
                elif event.key == pygame.K_6:
                    load_file_path = 'output_image.dcm'
                    dicom_data, current_image_data = load_dicom_image(load_file_path)
                    print(f"Зображення завантажено з {load_file_path}.")
                    image_height, image_width = current_image_data.shape  

        glClear(GL_COLOR_BUFFER_BIT)
        display_image(current_image_data, image_width, image_height)

        if show_text:
            render_text(text_texture_id, text_width, text_height, 10, image_height - text_height - 10)

        if linear_transform:
            current_image_data = linear_transformation(original_image_data, scaling_factor, offset)
            if high_low_borders:
                current_image_data = change_pixel_range(current_image_data, lower_limit, upper_limit)
        elif high_low_borders:
            current_image_data = change_pixel_range(current_image_data, lower_limit, upper_limit)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
