import base64
import io
import json
import random
import string
from pathlib import Path
from typing import Union, Optional, List

from PIL import Image
from arcade import Texture

from animation import Animation


def get_random_string(length):
    # Choose from all lowercase and uppercase letters and digits
    characters = string.ascii_letters + string.digits
    # Create a random string of the given length
    random_string = ''.join(random.choice(characters) for i in range(length))
    return random_string


class Piskel:
    def __init__(self, file_path=None, images=None, width=None, height=None, frame_count=None, layer_names=None):
        if images is not None:
            self.name = get_random_string(20)
            self.layer_images = images
            self.width = width
            self.height = height
            self.frame_count = frame_count
        else:
            self.file_path = file_path
            self.name = file_path
            self.data = self.load_json_file()
            self.width = self.data['piskel']['width']
            self.height = self.data['piskel']['height']
            self.frame_count = max(json.loads(layer)['frameCount'] for layer in self.data['piskel']['layers'])
            self.layer_images = self.extract_images()  # Keeps a dictionary of images keyed by layer names

        self.combined_image = self.build_composite_image(layer_names)
        self.left = True

    def load_json_file(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def extract_images(self):
        images = {}
        for layer_json in self.data['piskel']['layers']:
            layer_data = json.loads(layer_json)
            for chunk in layer_data['chunks']:
                base64_png = chunk['base64PNG'].split(",")[1]
                image_data = base64.b64decode(base64_png)
                image = Image.open(io.BytesIO(image_data)).convert("RGBA")
                images[layer_data['name']] = image
        return images

    def build_composite_image(self, layer_names=None):
        combined_image = Image.new("RGBA", next(iter(self.layer_images.values())).size)
        if layer_names is None:
            for image in self.layer_images.values():
                combined_image = Image.alpha_composite(combined_image, image)
        else:
            for name in layer_names:
                if name in self.layer_images:
                    combined_image = Image.alpha_composite(combined_image, self.layer_images[name])
        return combined_image

    def rebuild_composite_image(self, layer_names=None):
        self.combined_image = self.build_composite_image(layer_names)

    def get_frame(self, frame_number):
        left = (frame_number - 1) * self.width
        top = 0
        right = left + self.width
        bottom = top + self.height
        return self.combined_image.crop((left, top, right, bottom))

    def get_frames(self, num_frames=None):
        num_frames = num_frames or self.frame_count
        frames = []
        for i in range(num_frames):
            frames.append(self.get_frame(i + 1))
        return frames

    @property
    def layer_names(self):
        return list(self.layer_images.keys())

    @classmethod
    def combine_piskels(cls, piskels_with_layers):
        # Check consistent frame count
        frame_counts = {piskel.frame_count for piskel, _ in piskels_with_layers}
        if len(frame_counts) > 1:
            raise RuntimeError("Frame counts are not consistent across all piskels.")

        # Check consistent frame width
        widths = {piskel.width for piskel, _ in piskels_with_layers}
        if len(widths) > 1:
            raise RuntimeError("Widths are not consistent across all piskels.")

        # Check consistent frame height
        heights = {piskel.height for piskel, _ in piskels_with_layers}
        if len(heights) > 1:
            raise RuntimeError("Heights are not consistent across all piskels.")

        combined_images = {}
        for name in piskels_with_layers[0][0].layer_names:
            for piskel, chosen_layers in piskels_with_layers:
                if name in chosen_layers:
                    combined_images[name] = piskel.layer_images[name]

        base_piskel = piskels_with_layers[0][0]  # Using the first piskel for dimensions and frame count
        return cls(images=combined_images, width=base_piskel.width, height=base_piskel.height,
                   frame_count=base_piskel.frame_count)

    def get_animation(self, frame_time):
        return Animation(
            file_path=self.load_as_spritesheet(),
            frame_width=self.width,
            frame_height=self.height,
            columns=self.frame_count,
            frame_count=self.frame_count,
            frame_duration=frame_time,
            scale=1.0,
            loop=False,
            margin_x=-9 if self.left else 9
        )

    def load_as_spritesheet(self, hit_box_algorithm: Optional[str] = "Simple", hit_box_detail: float = 4.5) -> List[Texture]:
        """
        :param str hit_box_algorithm: One of None, 'None', 'Simple' (default) or 'etailed'.
        :param float hit_box_detail: Float, defaults to 4.5. Used with 'Detailed' to hit box
        :returns List: List of :class:`Texture` objects.
        """

        texture_list = []

        source_image = self.combined_image
        margin = 0
        for sprite_no in range(self.frame_count):
            row = sprite_no // self.frame_count
            column = sprite_no % self.frame_count
            start_x = (self.width + margin) * column
            start_y = (self.height + margin) * row
            image = source_image.crop((start_x, start_y, start_x + self.width, start_y + self.height))
            texture = Texture(
                f"{self.name}-{sprite_no}",
                image=image,
                hit_box_algorithm=hit_box_algorithm,
                hit_box_detail=hit_box_detail,
            )
            texture_list.append(texture)

        return texture_list

    def fliplr(self, update_image=True):
        """Flip each frame horizontally and optionally update the combined image."""
        flipped_frames = [frame.transpose(Image.FLIP_LEFT_RIGHT) for frame in self.get_frames()]
        if update_image:
            # Rebuild the combined image from flipped frames, placing them side by side
            new_combined_image = Image.new("RGBA", (self.width * self.frame_count, self.height))
            for index, frame in enumerate(flipped_frames):
                x_offset = index * self.width  # Calculate horizontal offset
                new_combined_image.paste(frame, (x_offset, 0))
            self.combined_image = new_combined_image
            self.left = not self.left
        return flipped_frames
