from matplotlib import pyplot as plt

from piskel import Piskel


def main(piskel_files, layers_lists):
    piskels_with_layers = [(Piskel(file), layers) for file, layers in zip(piskel_files, layers_lists)]
    combined_piskel = Piskel.combine_piskels(piskels_with_layers)
    plt.imshow(combined_piskel.combined_image)
    plt.show()

    combined_piskel.fliplr()
    plt.imshow(combined_piskel.combined_image)
    plt.show()


    # frames = combined_piskel.get_frames()
    # for i, frame in enumerate(frames):
    #     frame.save(f'temp_frames_test/combined_frame_{i + 1}.png')


if __name__ == "__main__":
    piskel_filenames = [
        r"..\battlefield\piksel_files\20240827_walk_with_sword-20240827-163437.piskel",
        r"..\battlefield\piksel_files\20240827_farmer_walk_with_pitchfork-20240828-230937.piskel"
    ]
    piskel_filenames = [
        r"..\battlefield\piksel_files\main_character\large_sword_attack.piskel",
        r"..\battlefield\piksel_files\20240827_farmer_attack-20240909-165006.piskel"
    ]
    layers_from_piskels = [
        ['Torso', 'Head'],
        ["Sword", 'Left arm', 'Right arm', 'Left leg', 'Right leg'],
    ]
    main(piskel_filenames, layers_from_piskels)
