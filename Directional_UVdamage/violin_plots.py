# violin plots module

# Standalone (cet-independent) paper analysis script.
# Loads a nuclei halves df, tags each row with its
# condition, and plots the top/bottom CPD intensity
# ratio as a violin plot split by embryo age group,
# annotated with a Mann-Whitney significance test.

__author__ = 'Angelo Angonezi'
__email__ = 'angelo.angonezi@unibas.ch'
__affiliation__ = 'University of Basel'

######################################################################
# imports

from os.path import join
from pandas import Series
from pandas import read_csv
from pandas import DataFrame
from seaborn import set_theme
from seaborn import violinplot
from seaborn import set_context
from argparse import ArgumentParser
from matplotlib import pyplot as plt
from statannotations.Annotator import Annotator

######################################################################
# defining global variables

context = 'paper'
conditions_dict = {'N2': 'wt',
                   'SM': 'cec-4, emr-1',
                   'GW': 'met-2, set-25'}
FONT_DICT = {'fontsize': 16}

######################################################################
# argument parsing related functions


def get_args_dict() -> dict:
    """
    Parses the arguments and returns a dictionary of the arguments.
    :return: Dictionary. Represents the parsed arguments.
    """
    # defining program description
    description = 'violin plots module'

    # creating a parser instance
    parser = ArgumentParser(description=description)

    # adding arguments to parser

    # input path param
    parser.add_argument('-i', '--input-path',
                        dest='input_path',
                        type=str,
                        required=False,
                        help='defines path to input nuclei halves df [.csv]')

    # output folder param
    parser.add_argument('-o', '--output-folder',
                        dest='output_folder',
                        type=str,
                        required=False,
                        help='defines path to output folder (will contain top/bottom ratio figure [.pdf])')

    # creating arguments dictionary
    args_dict = vars(parser.parse_args())

    # returning the arguments dictionary
    return args_dict

######################################################################
# defining auxiliary functions


def add_col(df: DataFrame,
            col_name: str,
            func,
            func_kwargs: dict | None = None
            ) -> None:
    """
    Given a dataframe, adds new column
    to df, based on given column name
    and data acquisition function.
    """
    # defining placeholder value for new col
    new_col = []

    # getting df rows
    df_rows = df.iterrows()

    # iterating over df rows
    for row_index, row_data in df_rows:

        # checking if func kwargs is not none
        if func_kwargs:

            # getting current row new col value
            current_value = func(row_data=row_data,
                                 **func_kwargs)

        else:

            # getting current row new col value
            current_value = func(row_data=row_data)

        # appending current value to new col
        new_col.append(current_value)

    # adding col to df
    df[col_name] = new_col


def get_condition(row_data: Series,
                  conditions_dict: dict
                  ) -> str:
    """
    Given an embryos df row data,
    returns condition ("UVB", or the
    image name prefix plus its
    genotype details, e.g. "N2 (wt)").
    """
    # getting current row info
    image_name = row_data['image_name']

    # getting is bools
    is_uvb = ('UVB' in image_name)

    # checking wt bool
    if is_uvb:

        # updating condition
        condition = 'UVB'

    else:

        # getting image name prefix
        name_prefix = image_name[0:2]

        # getting condition details
        condition_details = conditions_dict[name_prefix]

        # updating condition
        condition = f'{name_prefix} ({condition_details})'

    # returning condition
    return condition


def plot_violin(ratios_df: DataFrame,
                output_folder: str
                ) -> None:
    """
    Given a ratios df, plots violin of
    top/bottom CPD intensity ratio,
    split by embryo age group and
    annotated with a Mann-Whitney
    significance test; the df's
    "condition" col is not used here.
    """
    set_theme()
    set_context(context=context)

    # setting figure size
    plt.figure(figsize=(12, 8))

    # plotting violin
    ax = violinplot(data=ratios_df,
                    x='embryo_age_group',
                    y='top_bottom_ratio',
                    hue='embryo_age_group',
                    order=['young', 'old'],
                    hue_order=['young', 'old'],
                    legend='auto',
                    cut=0,
                    bw_adjust=1.8,
                    gridsize=500)

    # defining pairs to compare
    pairs = [(('young',),
              ('old',))]

    # creating annotator
    annotator = Annotator(ax=ax,
                          pairs=pairs,
                          data=ratios_df,
                          x='embryo_age_group',
                          y='top_bottom_ratio',
                          hue='embryo_age_group',
                          order=['young', 'old'],
                          hue_order=['young', 'old'])

    # configuring annotator
    annotator.configure(test='Mann-Whitney',
                        text_format='star',
                        loc='outside',
                        verbose=True)

    # setting figure legends
    plt.xlabel(xlabel='Embryo age group',
               fontdict=FONT_DICT)
    plt.ylabel(ylabel='Nuclear Top/Bottom CPD intensity ratio',
               fontdict=FONT_DICT)

    # adding stats annotations
    annotator.apply_and_annotate()

    # assembling save path
    save_name = 'violins.pdf'
    save_path = join(output_folder,
                     save_name)

    # saving figure
    plt.savefig(save_path,
                dpi=300)

######################################################################
# defining main pipeline function


def run_analysis(input_path: str,
                 output_folder: str
                 ) -> None:
    """
    Given input path and output folder, runs
    the currently active top/bottom ratio
    analysis end to end: loads the nuclei
    halves df (expected to already carry a
    precomputed "top_bottom_ratio" and
    "embryo_age_group" col), tags each row
    with its condition, then plots the
    resulting violin figure into the given
    output folder.
    """
    # loading df
    print('loading df...')
    halves_df = read_csv(input_path)

    # adding cols
    print('adding cols...')
    add_col(df=halves_df,
            col_name='condition',
            func=get_condition,
            func_kwargs={'conditions_dict': conditions_dict})

    # plotting data
    print('plotting data...')
    plot_violin(ratios_df=halves_df,
                output_folder=output_folder)

    # printing execution message
    print('analysis complete!')

######################################################################
# defining main function


def main():
    """Runs main code."""
    # getting args dict
    args_dict = get_args_dict()

    # getting input path
    input_path = args_dict['input_path']

    # getting output folder
    output_folder = args_dict['output_folder']

    # running analysis
    run_analysis(input_path=input_path,
                 output_folder=output_folder)

######################################################################
# running main function


if __name__ == '__main__':
    main()

######################################################################
# end of current module
