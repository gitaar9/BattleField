import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import numpy as np

def open_image():
    filepath = filedialog.askopenfilename()
    if not filepath:
        return

    image = Image.open(filepath)
    img_label.original_image = image
    update_image_with_grid()

def update_image_with_grid():
    if not hasattr(img_label, 'original_image'):
        return

    image = img_label.original_image.copy()
    width, height = image.size
    cols = columns_slider.get()
    rows = rows_slider.get()

    # Draw grid
    draw_image = image.copy()
    draw = ImageDraw.Draw(draw_image)
    for i in range(1, cols):
        draw.line((i * width // cols, 0, i * width // cols, height), fill="red", width=2)
    for i in range(1, rows):
        draw.line((0, i * height // rows, width, i * height // rows), fill="red", width=2)

    img_label.grid_image = draw_image
    img_label.photo = ImageTk.PhotoImage(draw_image)
    img_label.config(image=img_label.photo)

def apply_grid():
    if not hasattr(img_label, 'original_image'):
        return

    image = img_label.original_image.copy()
    width, height = image.size
    cols = columns_slider.get()
    rows = rows_slider.get()

    grid_width = width // cols
    grid_height = height // rows

    pixels = np.array(image)

    # Create a new image with size equal to the grid size
    new_image = Image.new("RGB", (cols, rows))

    for row in range(rows):
        for col in range(cols):
            x_start = col * grid_width
            y_start = row * grid_height
            x_end = min((col + 1) * grid_width, width)
            y_end = min((row + 1) * grid_height, height)

            # Extract the block of pixels
            block = pixels[y_start:y_end, x_start:x_end]

            # Calculate the average color
            avg_color = np.mean(block.reshape(-1, 3), axis=0).astype(int)
            avg_color = tuple(avg_color)

            # Set the color in the new image
            new_image.putpixel((col, row), avg_color)

    img_label.new_image = new_image
    img_label.photo = ImageTk.PhotoImage(new_image.resize((width, height), Image.NEAREST))
    img_label.config(image=img_label.photo)

def save_image():
    if hasattr(img_label, 'new_image'):
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if save_path:
            img_label.new_image.save(save_path)

# Setup the main application window
root = tk.Tk()
root.title("Image Grid Overlay")

# Create a label to display the image
img_label = tk.Label(root)
img_label.pack()

# Create sliders for columns and rows
columns_slider = tk.Scale(root, from_=1, to=100, orient=tk.HORIZONTAL, label="Columns", command=lambda _: update_image_with_grid())
columns_slider.set(10)
columns_slider.pack(side=tk.LEFT, padx=5, pady=5)

rows_slider = tk.Scale(root, from_=1, to=100, orient=tk.HORIZONTAL, label="Rows", command=lambda _: update_image_with_grid())
rows_slider.set(10)
rows_slider.pack(side=tk.LEFT, padx=5, pady=5)

# Create buttons
open_button = tk.Button(root, text="Open Image", command=open_image)
open_button.pack(side=tk.LEFT, padx=5, pady=5)

apply_button = tk.Button(root, text="Apply Grid", command=apply_grid)
apply_button.pack(side=tk.LEFT, padx=5, pady=5)

save_button = tk.Button(root, text="Save Image", command=save_image)
save_button.pack(side=tk.LEFT, padx=5, pady=5)

# Run the application
root.mainloop()
