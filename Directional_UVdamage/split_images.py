# split images module

# Standalone (cet-independent) paper analysis script.
# Given a folder of tif stacks, splits each image into
# top/bottom parts (according to a given denominator) and
# saves the two halves into top/bottom subfolders under a
# given output folder.

__author__ = 'Angelo Angonezi'
__email__ = 'angelo.angonezi@unibas.ch'
__affiliation__ = 'University of Basel'

######################################################################
# imports

from os import listdir
from os import makedirs
from os.path import join
from numpy import ndarray
from os.path import exists
from tifffile import imread
from tifffile import imwrite
from natsort import natsorted
from argparse import ArgumentParser

######################################################################
# argument parsing related functions


def get_args_dict() -> dict:
    """
    Parses the arguments and returns a dictionary of the arguments.
    :return: Dictionary. Represents the parsed arguments.
    """
    # defining program description
    description = 'split images module'

    # creating a parser instance
    parser = ArgumentParser(description=description)

    # adding arguments to parser

    # input folder param
    parser.add_argument('-i', '--input-folder',
                        dest='input_folder',
                        type=str,
                        required=True,
                        help='defines path to folder containing images [.tif]')

    # output folder param
    parser.add_argument('-o', '--output-folder',
                        dest='output_folder',
                        type=str,
                        required=True,
                        help='defines output folder (folder that will contain separate top/bottom images [.tif] - creates subfolders)')

    # denominator param
    parser.add_argument('-d', '--denominator',
                        dest='denominator',
                        type=int,
                        required=False,
                        default=2,
                        help='defines denominator to be used in splitting ("2" separates image in top/bottom halves, "3" top/bottom thirds, etc.)')

    # overwrite output param
    parser.add_argument('-ow', '--overwrite-output',
                        dest='overwrite_output',
                        action='store_true',
                        required=False,
                        help='defines whether overwrite files in output folder (skips existing output by default)')

    # creating arguments dictionary
    args_dict = vars(parser.parse_args())

    # returning the arguments dictionary
    return args_dict

######################################################################
# defining auxiliary functions


def load_image(input_path: str) -> ndarray:
    """
    Given a path to an image, returns
    image as numpy array.
    """
    # reading image
    image = imread(input_path)

    # returning image
    return image


def save_image(save_path: str,
               image: ndarray
               ) -> None:
    """
    Given an image, saves it
    to given save path.
    """
    # saving image
    imwrite(save_path,
            image)


def get_files_in_folder(input_folder: str,
                        extension: str = ''
                        ) -> list:
    """
    Given a path to a folder, returns a list containing
    all files in folder that match given extension.
    """
    # getting all files in folder
    all_files = listdir(input_folder)

    # getting specific files
    valid_files = [file                          # getting file
                   for file                      # iterating over files
                   in all_files                  # in input folder
                   if file.endswith(extension)]  # only if file matches given extension

    # sorting list
    valid_files = natsorted(valid_files)

    # returning list
    return valid_files


def get_skip_file_bool(file_path: str,
                       overwrite_output: bool
                       ) -> bool:
    """
    Given a file path, and a conditional
    bool, returns True if file should
    be skipped, or False otherwise.
    """
    # defining placeholder for skip file bool
    skip_file_bool = False

    # getting skip existing output bool
    skip_existing_output = (not overwrite_output)

    # checking whether to skip existing output
    if skip_existing_output:

        # getting file exists bool
        file_exists = exists(file_path)

        # checking if current output file already exists
        if file_exists:

            # updating skip file bool
            skip_file_bool = True

    # returning skip file bool
    return skip_file_bool


def split_image(input_path: str,
                top_output_path: str,
                bottom_output_path: str,
                denominator: int = 2
                ) -> None:
    """
    Given a path to an image, splits image in
    top/bottom parts (according to specified denominator),
    saving top and bottom portions to respective
    output paths.
    """
    # loading current image
    image = load_image(input_path=input_path)

    # getting image shape
    image_shape = image.shape

    # getting z-slices num (height of the image array)
    z_slices_num = image_shape[0]

    # calculating the size of a single fractional chunk
    chunk_size = (z_slices_num // denominator)

    # getting top image (from index 0 up to the end of the first chunk)
    top_index = 0
    top_image = image[top_index:chunk_size, :, :]

    # getting bottom image (from the start of the final chunk to the end of the image)
    bottom_index = z_slices_num - chunk_size
    bottom_image = image[bottom_index:, :, :]

    # saving current images
    save_image(save_path=top_output_path,
               image=top_image)
    save_image(save_path=bottom_output_path,
               image=bottom_image)


def split_images(input_folder: str,
                 output_folder: str,
                 denominator: int,
                 overwrite_output: bool
                 ) -> None:
    """
    Given a path to a folder containing tif
    stacks, splits each image into top and
    bottom parts and saves them in subfolders
    created in given output folder.
    """
    # getting images in input folder
    images = get_files_in_folder(input_folder=input_folder,
                                 extension='.tif')

    # getting images num
    images_num = len(images)

    # getting current top/bottom folder paths
    top_folder = join(output_folder,
                      'top')
    bottom_folder = join(output_folder,
                         'bottom')

    # creating top/bottom subfolders
    makedirs(top_folder,
             exist_ok=True)
    makedirs(bottom_folder,
             exist_ok=True)

    # iterating over images in input folder
    for image_index, image_name in enumerate(images, start=1):

        # printing execution message
        f_string = f'splitting image {image_index}/{images_num}: {image_name}...'
        print(f_string)

        # getting current image input/output paths
        input_path = join(input_folder,
                          image_name)
        top_output_path = join(top_folder,
                               image_name)
        bottom_output_path = join(bottom_folder,
                                  image_name)

        # getting skip file bool
        skip_file = get_skip_file_bool(file_path=bottom_output_path,
                                       overwrite_output=overwrite_output)

        # checking whether to skip current file
        if skip_file:

            # skipping to next file
            continue

        # splitting current image
        split_image(input_path=input_path,
                    top_output_path=top_output_path,
                    bottom_output_path=bottom_output_path,
                    denominator=denominator)

    # printing execution message
    print('analysis complete!')

######################################################################
# defining main function


def main():
    """Runs main code."""
    # getting args dict
    args_dict = get_args_dict()

    # getting input folder
    input_folder = args_dict['input_folder']

    # getting output folder
    output_folder = args_dict['output_folder']

    # getting denominator
    denominator = args_dict['denominator']

    # getting overwrite output flag
    overwrite_output = args_dict['overwrite_output']

    # running split_images function
    split_images(input_folder=input_folder,
                 output_folder=output_folder,
                 denominator=denominator,
                 overwrite_output=overwrite_output)

######################################################################
# running main function


if __name__ == '__main__':
    main()

######################################################################
# end of current module
