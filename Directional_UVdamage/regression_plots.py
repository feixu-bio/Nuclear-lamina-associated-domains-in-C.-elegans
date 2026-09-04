# regression plots module

# Standalone (cet-independent) paper analysis script.
# Loads a nuclei summary df, filters it down to the
# analysis population, and fits/report per-condition
# log-linear regressions of CPD intensity against the
# number of nuclei above each nucleus, including pairwise
# slope comparisons across conditions.

__author__ = 'Angelo Angonezi'
__email__ = 'angelo.angonezi@unibas.ch'
__affiliation__ = 'University of Basel'

######################################################################
# imports

import warnings
import numpy as np
import seaborn as sns
from os.path import join
from pandas import read_csv
import statsmodels.api as sm
from pandas import DataFrame
from seaborn import set_theme
from seaborn import set_context
import matplotlib.pyplot as plt
from itertools import combinations
from scipy.stats import linregress
from argparse import ArgumentParser
import statsmodels.formula.api as smf
from pandas.errors import PerformanceWarning
from statsmodels.stats.multitest import multipletests

# ignoring all pandas performance warnings
warnings.simplefilter(action='ignore', category=PerformanceWarning)

######################################################################
# defining global variables

conditions_dict = {'N2': 'wt',
                   'SM': 'cec-4, emr-1',
                   'GW': 'met-2, set-25'}
FIG_SIZE = (12, 8)

######################################################################
# argument parsing related functions


def get_args_dict() -> dict:
    """
    Parses the arguments and returns a dictionary of the arguments.
    :return: Dictionary. Represents the parsed arguments.
    """
    # defining program description
    description = 'regression plots module'

    # creating a parser instance
    parser = ArgumentParser(description=description)

    # adding arguments to parser

    # input path param
    parser.add_argument('-i', '--input-path',
                        dest='input_path',
                        type=str,
                        required=False,
                        default='.\\data_tmp\\camila\\lamina\\plots\\plots_df.csv',
                        help='defines path to input nuclei summary df [.csv]')

    # output folder param
    parser.add_argument('-o', '--output-folder',
                        dest='output_folder',
                        type=str,
                        required=False,
                        help='defines path to output folder (will contain regression figure [.pdf])')

    # creating arguments dictionary
    args_dict = vars(parser.parse_args())

    # returning the arguments dictionary
    return args_dict

######################################################################
# defining auxiliary functions


def get_p_value_str(p_val: float) -> str:
    """
    Given a p-value, returns its string
    representation (scientific notation
    below 0.001, fixed 3 decimal places
    otherwise).
    """
    # checking whether p-value is below scientific notation threshold
    if p_val < 0.001:

        # formatting p-value in scientific notation
        p_str = f'{p_val:.2e}'

    else:

        # formatting p-value with fixed decimal places
        p_str = f'{p_val:.3f}'

    # returning p-value string
    return p_str


def get_regression_stats_text(slope: float,
                              intercept: float,
                              r2: float,
                              p_str: str
                              ) -> str:
    """
    Given a regression's slope, intercept,
    r-squared, and formatted p-value string,
    returns the annotation text to be drawn
    on the regression plot.
    """
    # assembling stats text
    stats_text = f'$log(y) = {slope:.4f}x + {intercept:.2f}$\n'
    stats_text += f'$R^2 = {r2:.3f}$, $p = {p_str}$'

    # returning stats text
    return stats_text


def annotate_regression_stats(data: DataFrame,
                              x: str,
                              y: str,
                              **kwargs
                              ) -> None:
    """
    Given a (sub)df and x/y col names,
    fits a linear regression and draws
    the fit stats (slope, intercept, r2,
    p-value) as a text box in the current
    axis.
    """
    # getting current axis
    ax = plt.gca()

    # dropping rows with missing values in x/y cols
    valid_df = data[[x, y]].dropna()

    # getting valid rows num
    valid_rows_num = len(valid_df)

    # checking whether there are enough points to fit a regression
    if valid_rows_num <= 1:

        # skipping annotation
        return

    # fitting linear regression
    slope, intercept, r_val, p_val, std_err = linregress(x=valid_df[x],
                                                          y=valid_df[y])

    # getting r-squared
    r2 = r_val ** 2

    # getting p-value string
    p_str = get_p_value_str(p_val=p_val)

    # getting stats text
    stats_text = get_regression_stats_text(slope=slope,
                                           intercept=intercept,
                                           r2=r2,
                                           p_str=p_str)
    print(stats_text)

    # defining text box style
    box_style = dict(boxstyle='round,pad=0.5',
                     facecolor='white',
                     alpha=0.75,
                     edgecolor='grey')

    # drawing stats text box in current axis
    ax.text(0.95,
            0.05,
            stats_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='bottom',
            horizontalalignment='right',
            bbox=box_style)


def plot_log_regression_with_stats(df: DataFrame,
                                   x_col: str,
                                   y_col: str,
                                   hue_col: str = None,
                                   hue_order: list = None,
                                   output_folder: str = '.',
                                   fig_size: tuple = (8, 6)
                                   ) -> None:
    """
    Given a df and x/y col names, plots a
    (optionally faceted, by hue col) log-linear
    regression of y col over x col, annotated
    with fit stats, and saves the resulting
    figure in given output folder.
    """
    set_theme()
    set_context(context='paper')

    # copying df
    plot_df = df.copy()

    # dropping rows with missing values in x/y cols
    plot_df = plot_df.dropna(subset=[x_col, y_col])

    # getting log-transformed y col name
    target_y = f'{y_col}_log'

    # adding log-transformed y col
    plot_df[target_y] = np.log(plot_df[y_col])

    # getting hue col in df bool
    hue_col_in_df = bool(hue_col) and (hue_col in plot_df.columns)

    # checking whether to plot faceted regression (one subplot per hue value)
    if hue_col_in_df:

        # creating facet grid (one column per hue value, in given order)
        grid = sns.FacetGrid(plot_df,
                             col=hue_col,
                             hue=hue_col,
                             col_order=hue_order,
                             hue_order=hue_order,
                             height=fig_size[1],
                             aspect=fig_size[0] / fig_size[1])

        # plotting regression in each facet
        grid.map_dataframe(sns.regplot,
                           x=x_col,
                           y=target_y,
                           scatter_kws={'alpha': 0.3})

        # annotating each facet with regression stats
        grid.map_dataframe(annotate_regression_stats,
                           x=x_col,
                           y=target_y)

        # setting axis labels
        grid.set_axis_labels('# Nuclei above',
                             'log(Nuclear CPD mean intensity)')

    else:  # single, unfaceted regression plot

        # creating figure
        plt.figure(figsize=fig_size)

        # plotting regression
        sns.regplot(data=plot_df,
                   x=x_col,
                   y=target_y,
                   scatter_kws={'alpha': 0.3})

        # annotating plot with regression stats
        annotate_regression_stats(data=plot_df,
                                  x=x_col,
                                  y=target_y)

        # setting y label
        plt.ylabel(f'log({y_col})')

    # getting hue suffix (only if hue col is defined)
    hue_suffix = f'_by_{hue_col}' if hue_col else ''

    # assembling save name/path
    save_name = f'regression.pdf'
    save_path = join(output_folder, save_name)

    # saving figure
    plt.savefig(save_path,
                dpi=300,
                bbox_inches='tight')
    plt.close()

    # printing execution message
    print(f'Saved annotated plot to: {save_path}')


def get_interaction_param(cond: str,
                          x_col: str,
                          hue_col: str,
                          ref_group: str
                          ) -> str | None:
    """
    Given a condition, and the regression
    formula's x/hue cols and reference group,
    returns the respective interaction
    coefficient name (None if condition is
    the reference group, since its interaction
    coefficient is zero by definition).
    """
    # checking whether current condition is reference group
    if cond == ref_group:

        # reference group has no interaction coefficient
        return None

    # assembling interaction coefficient name
    interaction_param = f"{x_col}:C({hue_col}, Treatment(reference='{ref_group}'))[T.{cond}]"

    # returning interaction coefficient name
    return interaction_param


def get_pairwise_slope_comparison(model,
                                  cond1: str,
                                  cond2: str,
                                  x_col: str,
                                  hue_col: str,
                                  ref_group: str
                                  ) -> dict:
    """
    Given a fitted OLS model and a pair of
    conditions, runs a t-test contrast between
    their slopes and returns the comparison
    results as a dict.
    """
    # getting current pair interaction coefficient names
    p1 = get_interaction_param(cond=cond1, x_col=x_col, hue_col=hue_col, ref_group=ref_group)
    p2 = get_interaction_param(cond=cond2, x_col=x_col, hue_col=hue_col, ref_group=ref_group)

    # assembling hypothesis string (e.g. "param1 - param2 = 0" or "param1 = 0")
    if p1 is None:

        # comparing reference group against cond2
        hypothesis = f'{p2} = 0'

    elif p2 is None:

        # comparing cond1 against reference group
        hypothesis = f'{p1} = 0'

    else:

        # comparing cond1 against cond2
        hypothesis = f'{p1} - {p2} = 0'

    # printing hypothesis
    print(hypothesis)

    # running t-test contrast
    t_test_res = model.t_test(hypothesis)

    # getting t-test results
    slope_diff = float(t_test_res.effect.item())
    std_err = float(t_test_res.sd.item())
    t_stat = float(t_test_res.tvalue.item())
    p_val = float(t_test_res.pvalue.item())

    # assembling comparison dict
    comparison_dict = {'Comparison': f'{cond1} vs {cond2}',
                       'Slope Difference': slope_diff,
                       'Std Err': std_err,
                       't statistic': t_stat,
                       'p-value (raw)': p_val}

    # returning comparison dict
    return comparison_dict


def test_slope_differences_multiple(df: DataFrame,
                                    x_col: str,
                                    y_col: str,
                                    hue_col: str,
                                    ref_group: str = "N2 (wt)"
                                    ) -> tuple:
    """
    Given a df, fits an interaction model
    (log y col over x col, interacting with
    hue col) and performs pairwise slope
    comparisons across all condition pairs,
    returning the fitted model, anova table,
    and pairwise comparisons df.
    """
    # dropping rows with missing values in relevant cols
    data = df.copy().dropna(subset=[x_col, y_col, hue_col])

    # adding log y col
    data["log_y"] = np.log(data[y_col])

    # assembling ols formula string
    formula = f"log_y ~ {x_col} * C({hue_col}, Treatment(reference='{ref_group}'))"

    # fitting ols model
    model = smf.ols(formula=formula, data=data).fit()

    print("=== MODEL SUMMARY ===")
    print(model.summary())

    # getting anova table (testing overall interaction significance)
    print("\n=== ANOVA TABLE (Testing Overall Interaction Significance) ===")
    anova_table = sm.stats.anova_lm(model, typ=2)
    print(anova_table)

    print("\n=== PAIRWISE SLOPE COMPARISONS ===")

    # getting all unique conditions
    unique_conditions = data[hue_col].unique().tolist()

    # getting all condition pairs
    condition_pairs = list(combinations(unique_conditions, 2))

    # defining placeholder for pairwise results
    pairwise_results = []

    # iterating over condition pairs
    for cond1, cond2 in condition_pairs:

        # getting current pair slope comparison
        comparison_dict = get_pairwise_slope_comparison(model=model,
                                                        cond1=cond1,
                                                        cond2=cond2,
                                                        x_col=x_col,
                                                        hue_col=hue_col,
                                                        ref_group=ref_group)

        # appending current comparison to pairwise results
        pairwise_results.append(comparison_dict)

    # assembling pairwise df
    pairwise_df = DataFrame(pairwise_results)

    # applying bonferroni correction for multiple testing
    _, p_adj, _, _ = multipletests(pairwise_df["p-value (raw)"],
                                   alpha=0.05,
                                   method="bonferroni")
    pairwise_df["p-value (Bonferroni)"] = p_adj

    print(pairwise_df.to_string(index=False))

    # returning model, anova table and pairwise df
    return model, anova_table, pairwise_df


def save_statistics(stats_output: tuple,
                    output_folder: str,
                    prefix: str = "cpd_depth_analysis"
                    ) -> None:
    """
    Given the model/anova/pairwise stats
    output, saves the anova table, pairwise
    t-test comparisons, and ols coefficients
    as csvs in given output folder.
    """
    # unpacking model and tables
    model, anova_table, pairwise_df = stats_output

    # saving anova table
    anova_path = join(output_folder, f"{prefix}_anova_table.csv")
    anova_table.to_csv(anova_path, index=True)
    print(f"Saved ANOVA table -> {anova_path}")

    # saving pairwise t-test comparisons table
    pairwise_path = join(output_folder, f"{prefix}_pairwise_ttests.csv")
    pairwise_df.to_csv(pairwise_path, index=False)
    print(f"Saved Pairwise t-test table -> {pairwise_path}")

    # assembling ols coefficients df
    ols_coef_df = DataFrame({"coef": model.params,
                            "std_err": model.bse,
                            "t_value": model.tvalues,
                            "p_value": model.pvalues,
                            "conf_lower": model.conf_int()[0],
                            "conf_upper": model.conf_int()[1]})

    # saving ols coefficients table
    ols_path = join(output_folder, f"{prefix}_ols_coefficients.csv")
    ols_coef_df.to_csv(ols_path, index=True)
    print(f"Saved OLS coefficients table -> {ols_path}")

    # printing execution message
    print("All statistics successfully exported!")

######################################################################
# defining main pipeline function


def run_analysis(input_path: str,
                 output_folder: str
                 ) -> None:
    """
    Given input/output paths, runs the
    currently active nuclei-vs-depth
    regression analysis end to end:
    loads the nuclei summary df, fits
    per-condition log-linear regressions
    (with pairwise slope comparisons),
    plots the annotated regressions, and
    saves the resulting statistics tables.
    """
    # loading df
    print('loading df...')
    df = read_csv(input_path)

    # defining plot cols
    x_col = 'nuclei_above_count'
    y_col = 'cpd_mean_intensity_bg_removed'
    hue_col = 'condition'

    # getting hue order
    hue_order = [f'{condition} ({condition_details})'  # getting condition label
                for condition, condition_details        # iterating over condition/details pairs
                in conditions_dict.items()]              # in conditions dict

    # plotting regressions
    print('plotting regressions...')
    plot_log_regression_with_stats(df=df,
                                   x_col=x_col,
                                   y_col=y_col,
                                   hue_col=hue_col,
                                   hue_order=hue_order,
                                   output_folder=output_folder,
                                   fig_size=FIG_SIZE)

    # running regression stats
    print('running slope difference statistics...')
    stats_output = test_slope_differences_multiple(df=df,
                                                   x_col=x_col,
                                                   y_col=y_col,
                                                   hue_col=hue_col)

    # printing anova table
    print(stats_output[1])

    # printing pairwise comparisons table
    print(stats_output[2])

    # saving statistics
    save_statistics(stats_output=stats_output,
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
