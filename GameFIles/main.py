import time
import os
import random as ran
import sys

import tensorflow as tf
from tensorflow import keras

import numpy as np
import pygame.font, pygame.event, pygame.draw


pygame.init()

black = (0, 0, 0)
gray = (200, 200, 215)
blue_gray = (45, 45, 60)
white = (255, 255, 255)
orange = (255, 128, 10)
bright_orange = (255, 170, 50)
red = (255, 0, 0)

width, height = 914, 612
size = [width, height]
half_width, half_height = width/2, height/2
input_field = (392, 392)
edge_buffer = (10, 50)
scale_size = 17.6

x_coordinates =[]
y_coordinates = []
pixel_colors = []

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Convolutional Neural Network")

loading_background = pygame.Surface(size)
loading_background.fill(gray)
backdrop = pygame.Surface(size)
backdrop.fill(gray)
background = pygame.Surface(input_field)
background.fill(white)
background2 = pygame.Surface((492, 492))
background2.fill(white)

font = pygame.font.SysFont("Agency FB", 40)
font_small = pygame.font.SysFont("Agency FB", 32)
clock = pygame.time.Clock()

def calculate_image(background):
    """transforms the image into an array ready for matmult"""

    scaledBackground = pygame.transform.smoothscale(background, (28, 28))
    image = pygame.surfarray.array3d(scaledBackground)
    image = abs(1 - image / 253)
    image = np.mean(image, 2)

    pixelate(image)

    # Add a fourth dimension to the image to match the expected shape
    image_with_channels = np.expand_dims(image, axis=-1)
    image_with_channels = np.repeat(image_with_channels, 4, axis=-1)  # Assuming RGB channels
    image_with_batch = np.expand_dims(image_with_channels, axis=0)  # Add batch dimension
    return image_with_batch


def display_prediction(prediction, prob):
    """ displays the prediction and probability on screen """

    display_prediction = "Prediction: %s" %(prediction)
    display_probability = "Probability: %s" %(prob)
    font = pygame.font.SysFont("Agency FB", 36)

    # converts to pygame format
    initialize_prediction = font.render(display_prediction, 1, (white))
    initialize_probability = font.render(display_probability + "%", 1, (white))

    # draws to screen
    pygame.draw.rect(screen, orange, (edge_buffer[0], input_field[1] + edge_buffer[1] + 10, input_field[0], 90))
    screen.blit(initialize_prediction, (edge_buffer[0] + 5, input_field[1] + edge_buffer[1] + 20))
    screen.blit(initialize_probability, (edge_buffer[0] + 5, input_field[1] + edge_buffer[1] + 60))

def pixelate(image):
    """Pixelates image"""

    size = 28

    # Create RGB values for each pixel
    image = (255 - image * 255).astype(np.uint8)  # Assuming the image is already in grayscale

    # Draw rect for each pixel
    for row in range(size):
        for column in range(size):
            base_rgb = int(image[row, column])

            # Append coordinates and pixel colors
            x_coordinates.append(row)
            y_coordinates.append(column)
            pixel_colors.append(base_rgb)

def draw_gradient():
    """ draws a gradient background """

    gradient = [230, 230, 255]
    x = 0

    for i in range(int(size[0]/4 + 1)):

        pygame.draw.rect(screen, gradient, (x, 0, 4, size[1]))
        gradient[0] -= 0.55
        gradient[1] -= 0.55
        gradient[2] -= 0.55
        x += 4

    pygame.display.flip()



def calculate_prediction(image):
    new_model = tf.keras.models.load_model('SavedModels/NN.h5')
    prediction = new_model.predict(image)
    prediction_class = np.argmax(prediction)
    probability = round(np.max(prediction) * 100, 2)
    print(new_model.predict(image))
    # Display the prediction and probability
    display_prediction(prediction_class, probability)

def scanner():
    """ Creates visual scanner for user input """

    changeY = 0
    speed = 0.003

    # Used to call values that store data for each pixel
    coordinate_x = 1
    coordinate_y = 1
    px = 1

    for x in range(int(input_field[0] / 2)):

        # Draw background each time to overdraw scanner
        screen.blit(background, (edge_buffer))
        pygame.draw.rect(screen, red, (edge_buffer[0], edge_buffer[1] + changeY, input_field[0], 5))
        changeY += 2

        # Every 7 iterations, draw a line of pixelated image
        if changeY % 14 == 0:

            # Stagger the pixelated image
            if (changeY / 14) % 2 == 0:
                coordinate_x += 1
                coordinate_y += 1
                px += 1
            else:
                coordinate_x -= 1
                coordinate_y -= 1
                px -= 1

            for i in range(14):
                # Check if the index is within the valid range
                if px < len(pixel_colors):
                    gray_scaled = (pixel_colors[px], pixel_colors[px], pixel_colors[px])
                    pygame.draw.rect(screen, gray_scaled, (
                        x_coordinates[coordinate_x] * scale_size + input_field[0] + 2 * edge_buffer[0],
                        y_coordinates[coordinate_y] * scale_size + edge_buffer[1], scale_size, scale_size))
                coordinate_x += 2
                coordinate_y += 2
                px += 2

        # Draw rectangle same as background to compensate for overlap of scanner
        pygame.draw.rect(screen, gray, (edge_buffer[0], edge_buffer[1] + input_field[1], input_field[0], 10))

        # Update the screen
        time.sleep(speed)
        pygame.display.flip()

    # Goes from down to up
    coordinate_x = 783
    coordinate_y = 783
    px = 783

    for x in range(int(input_field[0] / 2)):

        screen.blit(background, (edge_buffer))
        pygame.draw.rect(screen, red, (edge_buffer[0], edge_buffer[1] + changeY, input_field[0], 5))
        changeY -= 2

        # Every 7 iterations, draw a line of pixelated image
        if changeY % 14 == 0:

            # Stagger the pixelated image, opposite of the first scanner
            if (changeY / 14) % 2 == 0:
                coordinate_x += 1
                coordinate_y += 1
                px += 1
            else:
                coordinate_x -= 1
                coordinate_y -= 1
                px -= 1

            # Fill in remaining pixels on the way up
            for i in range(14):
                # Check if the index is within the valid range
                if px < len(pixel_colors):
                    gray_scaled = (pixel_colors[px], pixel_colors[px], pixel_colors[px])
                    pygame.draw.rect(screen, gray_scaled, (
                        x_coordinates[coordinate_x] * scale_size + input_field[0] + 2 * edge_buffer[0],
                        y_coordinates[coordinate_y] * scale_size + edge_buffer[1], scale_size, scale_size))
                coordinate_x -= 2
                coordinate_y -= 2
                px -= 2

        # Prevent scanner from going past background and staying on screen
        pygame.draw.rect(screen, gray, (edge_buffer[0], edge_buffer[1] + input_field[1], input_field[0], 10))

        # Update screen at a set pace
        time.sleep(speed)
        pygame.display.flip()

    # Clear lists holding pixel data
    x_coordinates[:] = []
    y_coordinates[:] = []
    pixel_colors[:] = []

def create_button(btn_label, surface, color, new_color, locationX, locationY, width, height):
    """ creates interactive classify btn """

    # convert label to pygame format
    initialize_btn_label = font_small.render(btn_label, 1, white)
    initialize_btn_label_dim = initialize_btn_label.get_rect().width, initialize_btn_label.get_rect().height
    pygame.draw.rect(surface, color, (locationX, locationY, width, height))
    mouse = pygame.mouse.get_pos()

    # checks if mouse is with in boundaries of buttton and updates color
    if locationX + width > mouse[0] > locationX and locationY + height> mouse[1] > locationY:
        pygame.draw.rect(surface, new_color, (locationX, locationY, width, height))

        # if classify btn is clicked
        if pygame.mouse.get_pressed() == (1, 0, 0) and btn_label == "Classify":
            image = calculate_image(background)
            scanner()
            calculate_prediction(image)

        # if clear btn is clicked
        elif pygame.mouse.get_pressed() == (1, 0, 0) and btn_label == "Clear":

            # resets both canvases and predictions
            background.fill(white)
            screen.blit(background2, (2*edge_buffer[0] + input_field[0], edge_buffer[1]))
            display_prediction('Unknown', "0")

    else:
        pygame.draw.rect(surface, color, (locationX, locationY, width, height))

    # adds the btn label to the btn
    surface.blit(initialize_btn_label, (locationX + width/2 - initialize_btn_label_dim[0]/2,
        locationY + height/2 - initialize_btn_label_dim[1]/2))

def draw_line(surface, color, start, end, radius):
    """ draws a line """

    dx = end[0]-start[0]
    dy = end[1]-start[1]
    distance = max(abs(dx), abs(dy))

    for i in range(distance):
        x = int(start[0]+i/distance*dx)
        y = int(start[1]+i/distance*dy)
        pygame.draw.circle(surface, color, (x - edge_buffer[0], y - edge_buffer[1]), radius)
    pygame.display.flip()

def draw_interface():
    """ draws main components of interface """

    display_prediction('Unknown', "0")

    label_input = "Input"
    label_pixelated = "Pixelated"
    label_mnist = "Model trained on the 1000 students from campus"

    # convert to pygame format
    initialize_label_input = font.render(label_input, 1, black)
    initialize_label_pixelated = font.render(label_pixelated, 1, black)
    initialize_label_mnist = font.render(label_mnist, 1, white)

    # add to screen
    screen.blit(initialize_label_input, (edge_buffer[0] + 10, 10))
    screen.blit(initialize_label_pixelated, (input_field[0] + 2*edge_buffer[0] + 10, 10))
    pygame.draw.rect(screen, blue_gray, (edge_buffer[0], size[1] - 60, size[0] - 2*edge_buffer[0], 50))
    screen.blit(initialize_label_mnist, (size[0]/2 - initialize_label_mnist.get_rect().width/2, size[1] - 50))
    screen.blit(background2, (2*edge_buffer[0] + input_field[0], edge_buffer[1]))

    # update screen
    pygame.display.flip()

def main():
    """ draws interface """

    last_pos = (0, 0)
    line_width = 9

    draw_interface()

    image = None
    continue_on = True
    while continue_on:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed() == (1, 0, 0):
                    draw_line(background, black, event.pos, last_pos, line_width)
                last_pos = event.pos

            # update screen
        screen.blit(background, (edge_buffer[0], edge_buffer[1]))
        create_button("Classify", screen, orange, bright_orange, input_field[0] - 110, input_field[1] + edge_buffer[1] + 10, 120, 45)
        create_button("Clear", screen, orange, bright_orange, input_field[0] - 110, input_field[1] + edge_buffer[1] + 55, 120, 45)
        pygame.display.flip()

if __name__ == "__main__":
    main()