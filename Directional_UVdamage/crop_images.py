# crop images module

# Standalone (cet-independent) paper analysis script.
# Given a folder of images and an objects df (with either
# per-object "boundaries" or a "centroid" + fixed size),
# crops each object out of its source image and saves the
# crop to a given output folder.

__author__ = 'Angelo Angonezi'
__email__ = 'angelo.angonezi@unibas.ch'
__affiliation__ = 'University of Basel'

######################################################################
# imports

from os.path import join
from numpy import ndarray
from os.path import exists
from pandas import read_csv
from tifffile import imread
from tifffile import imwrite
from pandas import DataFrame
from argparse import ArgumentParser

######################################################################
# argument parsing related functions


def get_args_dict() -> dict:
    """
    Parses the arguments and returns a dictionary of the arguments.
    :return: Dictionary. Represents the parsed arguments.
    """
    # defining program description
    description = 'crop images module'

    # creating a parser instance
    parser = ArgumentParser(description=description)

    # adding arguments to parser

    # input folder param
    parser.add_argument('-i', '--input-folder',
                        dest='input_folder',
                        type=str,
                        required=True,
                        help='defines path to folder containing images [.tif]')

    # objects df path param
    parser.add_argument('-d', '--objects-df-path',
                        dest='objects_df_path',
                        type=str,
                        required=True,
                        help='defines path to objects df [.csv]')

    # margin param
    parser.add_argument('-m', '--margin',
                        dest='margin',
                        type=int,
                        required=False,
                        default=0,
                        help='defines margin (in pixels) to be applied in crop boundaries')

    # mask param
    parser.add_argument('-k', '--mask',
                        dest='mask',
                        action='store_true',
                        required=False,
                        help='defines whether images being cropped are masks (crops will only contain pixels matching object_id)')

    # fixed size param
    parser.add_argument('-f', '--fixed-size',
                        dest='fixed_size',
                        type=str,
                        required=False,
                        default=None,
                        help='defines whether to crop all images in a fixed size (z,y,x) based on centroid (overrides df boundaries)')

    # output folder param
    parser.add_argument('-o', '--output-folder',
                        dest='output_folder',
                        type=str,
                        required=True,
                        help='defines path to output folder (folder that will contain image crops [.tif])')

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


def filter_mask(mask: ndarray,
                object_id: int
                ) -> ndarray:
    """
    Given a mask with multiple ids,
    returns filtered mask containing
    only given id.
    """
    # defining placeholder for filtered mask
    filtered_mask = mask.copy()

    # removing pixels different from given id
    filtered_mask[mask != object_id] = 0

    # returning filtered mask
    return filtered_mask


def validate_min_boundary(value: int,
                          axis_min: int
                          ) -> int:
    """
    Given a min boundary value, and
    respective axis minimum, returns
    valid boundary value.
    """
    # if value is smaller than axis min
    if value < axis_min:

        # setting valid value as axis min
        return axis_min

    # returning valid value
    return value


def validate_max_boundary(value: int,
                          axis_max: int
                          ) -> int:
    """
    Given a max boundary value, and
    respective axis maximum, returns
    valid boundary value.
    """
    # if value is -1 (encodes for maximum dimension)
    if value == -1:

        # setting valid value as axis max
        return axis_max

    # if value is greater than axis max
    if value > axis_max:

        # setting valid value as axis max
        return axis_max

    # returning valid value
    return value


def crop_object(image: ndarray,
                boundaries: tuple,
                margin: int
                ) -> ndarray:
    """
    Given a loaded image, crop
    boundaries, and a margin, applies
    the margin to the boundaries,
    validates them, and returns
    cropped image.
    """
    # getting current image shape
    image_shape = image.shape

    # extracting coords from boundaries
    z_min, z_max, y_min, y_max, x_min, x_max = boundaries

    # adding margins (only if not set to max)
    z_min -= margin
    y_min -= margin
    x_min -= margin
    if z_max != -1:
        z_max += margin
    if y_max != -1:
        y_max += margin
    if x_max != -1:
        x_max += margin

    # getting dimensions num
    dimensions_num = image.ndim

    # checking dimensions num

    # multi-channel image (ZYXC)
    if dimensions_num == 4:

        # getting axis valid values
        z_axis_min = 0
        z_axis_max = image_shape[0]
        y_axis_min = 0
        y_axis_max = image_shape[1]
        x_axis_min = 0
        x_axis_max = image_shape[2]

        # validating boundaries
        z_min = validate_min_boundary(value=z_min, axis_min=z_axis_min)
        z_max = validate_max_boundary(value=z_max, axis_max=z_axis_max)
        y_min = validate_min_boundary(value=y_min, axis_min=y_axis_min)
        y_max = validate_max_boundary(value=y_max, axis_max=y_axis_max)
        x_min = validate_min_boundary(value=x_min, axis_min=x_axis_min)
        x_max = validate_max_boundary(value=x_max, axis_max=x_axis_max)

        # cropping image
        image_crop = image[z_min:z_max,  # z slices selection
                           y_min:y_max,  # y slices selection
                           x_min:x_max,  # x slices selection
                           :]            # all channels

    # single-channel image (ZYX)
    elif dimensions_num == 3:

        # getting axis valid values
        z_axis_min = 0
        z_axis_max = image_shape[0]
        y_axis_min = 0
        y_axis_max = image_shape[1]
        x_axis_min = 0
        x_axis_max = image_shape[2]

        # validating boundaries
        z_min = validate_min_boundary(value=z_min, axis_min=z_axis_min)
        z_max = validate_max_boundary(value=z_max, axis_max=z_axis_max)
        y_min = validate_min_boundary(value=y_min, axis_min=y_axis_min)
        y_max = validate_max_boundary(value=y_max, axis_max=y_axis_max)
        x_min = validate_min_boundary(value=x_min, axis_min=x_axis_min)
        x_max = validate_max_boundary(value=x_max, axis_max=x_axis_max)

        # cropping image
        image_crop = image[z_min:z_max,  # z slices selection
                           y_min:y_max,  # y slices selection
                           x_min:x_max]  # x slices selection

    # single-channel (2d projection)
    else:

        # getting axis valid values
        y_axis_min = 0
        y_axis_max = image_shape[0]
        x_axis_min = 0
        x_axis_max = image_shape[1]

        # validating boundaries
        y_min = validate_min_boundary(value=y_min, axis_min=y_axis_min)
        y_max = validate_max_boundary(value=y_max, axis_max=y_axis_max)
        x_min = validate_min_boundary(value=x_min, axis_min=x_axis_min)
        x_max = validate_max_boundary(value=x_max, axis_max=x_axis_max)

        # cropping image
        image_crop = image[y_min:y_max,  # y slices selection
                           x_min:x_max]  # x slices selection

    # returning crop
    return image_crop


def string_to_coords(coords_str: str) -> tuple:
    """
    Given a coords string "(Z, Y, X)", returns
    tuple of given values as ints (Z, Y, X).
    """
    # assembling coords tuple
    coords = eval(coords_str)

    # returning coords tuple
    return coords


def get_centroid_boundaries(coords: tuple,
                            bounding_dims: tuple
                            ) -> tuple:
    """
    Given a centroid coords and bounding
    size dimensions, returns respective
    boundaries.
    """
    # extracting coords from tuples
    z, y, x = coords
    z_dim, y_dim, x_dim = bounding_dims

    # getting radius from dims
    z_radius = z_dim // 2  # floor division, returns round down to nearest integer
    y_radius = y_dim // 2
    x_radius = x_dim // 2

    # getting min/max coord for each axis
    z_min = z - z_radius
    z_max = z + z_radius
    y_min = y - y_radius
    y_max = y + y_radius
    x_min = x - x_radius
    x_max = x + x_radius

    # assembling boundaries tuple
    boundaries = (z_min, z_max,
                  y_min, y_max,
                  x_min, x_max)

    # returning boundaries tuple
    return boundaries


def crop_objects(input_path: str,
                 df: DataFrame,
                 margin: int,
                 mask: bool,
                 output_folder: str,
                 fixed_size: str | None,
                 overwrite_output: bool
                 ) -> None:
    """
    Given a path to an image, and its
    respective objects df group, saves
    each object crop in given output
    folder.
    """
    # loading image
    image = load_image(input_path=input_path)

    # getting df rows
    df_rows = df.iterrows()

    # getting fixed size is none bool
    fixed_size_is_none = (fixed_size is None)

    # iterating over df rows
    for row_index, row_data in df_rows:

        # getting current row info
        crop_name = row_data['crop_name']

        # getting current crop output path
        output_path = join(output_folder,
                           crop_name)

        # getting skip file bool
        skip_file = get_skip_file_bool(file_path=output_path,
                                       overwrite_output=overwrite_output)

        # checking whether to skip current crop
        if skip_file:

            # skipping to next crop
            continue

        # checking whether crop should be in fixed size or use df boundaries

        if fixed_size_is_none:  # crop using df boundaries

            # getting boundaries from df
            boundaries_str = row_data['boundaries']

            # converting data types
            boundaries = string_to_coords(coords_str=boundaries_str)

        else:  # crop with fixed size

            # getting object centroid coords from df
            object_coords_str = row_data['centroid']

            # converting data types
            object_coords = string_to_coords(coords_str=object_coords_str)
            fixed_size_dims = string_to_coords(coords_str=fixed_size)  # noqa

            # getting fixed size boundaries
            boundaries = get_centroid_boundaries(coords=object_coords,
                                                 bounding_dims=fixed_size_dims)

        # cropping object
        current_crop = crop_object(image=image,
                                   boundaries=boundaries,
                                   margin=margin)

        # checking whether crop is mask
        if mask:

            # getting object id from df
            object_id = row_data['object_id']

            # filtering crop to contain only current object id pixels
            current_crop = filter_mask(mask=current_crop,
                                       object_id=object_id)

        # saving current crop
        save_image(save_path=output_path,
                   image=current_crop)


def crop_images(input_folder: str,
                objects_df_path: str,
                margin: int,
                mask: bool,
                output_folder: str,
                fixed_size: str | None,
                overwrite_output: bool
                ) -> None:
    """
    Given a path to a folder containing
    images, saves single object crops in
    given output folder, based on boundaries
    coordinates in given objects df.
    """
    # loading df
    print('loading objects df...')
    df = read_csv(objects_df_path)

    # defining group cols
    group_cols = ['image_name',
                  'image_index']

    # grouping df
    df_groups = df.groupby(group_cols)

    # getting images num
    images_num = len(df_groups)

    # iterating over df groups
    for group_index, group_item in enumerate(df_groups, start=1):

        # getting current group info
        df_name, df_group = group_item
        image_name, image_index = df_name

        # printing execution message
        f_string = f'cropping image {group_index}/{images_num}: {image_name} '
        f_string += f'({len(df_group)} crop(s))...'
        print(f_string)

        # getting current image path
        image_path = join(input_folder,
                          image_name)

        # cropping current image objects
        crop_objects(input_path=image_path,
                     df=df_group,
                     margin=margin,
                     mask=mask,
                     output_folder=output_folder,
                     fixed_size=fixed_size,
                     overwrite_output=overwrite_output)

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

    # getting objects df path
    objects_df_path = args_dict['objects_df_path']

    # getting margin
    margin = args_dict['margin']

    # getting mask bool
    mask = args_dict['mask']

    # getting output folder
    output_folder = args_dict['output_folder']

    # getting fixed size flag
    fixed_size = args_dict['fixed_size']

    # getting overwrite output flag
    overwrite_output = args_dict['overwrite_output']

    # running crop_images function
    crop_images(input_folder=input_folder,
                objects_df_path=objects_df_path,
                margin=margin,
                mask=mask,
                output_folder=output_folder,
                fixed_size=fixed_size,
                overwrite_output=overwrite_output)

######################################################################
# running main function


if __name__ == '__main__':
    main()

######################################################################
# end of current module
