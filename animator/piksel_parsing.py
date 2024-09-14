import json
import base64
from PIL import Image, ImageChops
import io
import argparse

from matplotlib import pyplot as plt


class Piskel:
    def __init__(self, file_path=None, images=None, width=None, height=None, frame_count=None):
        if file_path:
            self.file_path = file_path
            self.data = self.load_json_file()
            self.width = self.data['piskel']['width']
            self.height = self.data['piskel']['height']
            self.frame_count = max(json.loads(layer)['frameCount'] for layer in self.data['piskel']['layers'])
            self.layer_images = self.extract_images()  # Keeps a dictionary of images keyed by layer names
        else:
            self.layer_images = images
            self.width = width
            self.height = height
            self.frame_count = frame_count

        self.combined_image = self.build_composite_image()

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
    def combine_piskels(cls, piskel1, layer_names1, piskel2, layer_names2):
        if piskel1.frame_count == piskel2.frame_count:
            new_frame_count = piskel1.frame_count
        else:
            raise RuntimeError("frame count are not equal")

        combined_images = {}
        for name in piskel1.layer_names:
            if name in layer_names1:
                combined_images[name] = piskel1.layer_images[name]
            if name in layer_names2:
                combined_images[name] = piskel2.layer_images[name]

        return cls(images=combined_images, width=piskel1.width, height=piskel1.height, frame_count=new_frame_count)


def main(file_path1, layers1, file_path2, layers2):
    piskel1 = Piskel(file_path1)
    piskel2 = Piskel(file_path2)

    combined_piskel = Piskel.combine_piskels(piskel1, layers1, piskel2, layers2)
    plt.imshow(combined_piskel.combined_image)
    plt.show()

    frames = combined_piskel.get_frames()
    for i, frame in enumerate(frames):
        frame.save(f'combined_frame_{i + 1}.png')


if __name__ == "__main__":
    piskel_filenames = [
        r"..\battlefield\piksel_files\20240827_walk_with_sword-20240827-163437.piskel",
        r"..\battlefield\piksel_files\20240827_farmer_walk_with_pitchfork-20240828-230937.piskel"
    ]
    piskel_filenames = [
        r"..\battlefield\piksel_files\20240827_both_attacks-20240827-144047.piskel",
        r"..\battlefield\piksel_files\20240827_farmer_attack-20240909-165006.piskel"
    ]
    layers_from_piskels = [
        ['Torso', 'Head', 'Sword'],
        ['Left leg', 'Right leg', 'Left arm', 'Right arm']
    ]
    main(piskel_filenames[0], layers_from_piskels[0], piskel_filenames[1], layers_from_piskels[1])
