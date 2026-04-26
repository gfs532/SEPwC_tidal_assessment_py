# import the modules we need
import pandas as pd
import datetime
import os
import numpy as np
import uptide
import pytz
import math
from scipy import stats
import matplotlib.dates as mdates
import argparse
from pathlib import Path

def read_tidal_data(filename):

    #Create a path object.
    path = Path(filename)

    #Check the file exists.
    if not path.is_file():
        raise FileNotFoundError(f"Could not find the file: {filename}")

	#Put the data in a DataFrame.
	#Make sure whitespaces are not treated as columns.
	#Skip the first 11 rows.
	#Name the columns.
    df = pd.read_csv(
        filename,
        sep=r'\s+',
        skiprows=11,
        names=['Cycle', 'Date', 'Time', 'Sea Level', 'Residual']
    )

	#Combine date and time columns into one column.
    df['date_and_time'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

    return


def extract_single_year_remove_mean(year, data):

    return


def extract_section_remove_mean(start, end, data):

    return year_data


def join_data(data1, data2):

    return

def sea_level_rise(data):

    return

def tidal_analysis(data, constituents, start_datetime):

    return

def get_longest_contiguous_data(data):

    return


def main(args_list=None):

    parser = argparse.ArgumentParser(
                     prog="UK Tidal analysis",
                     description="Calculate tidal constiuents and RSL from tide gauge data",
                     )

    parser.add_argument("directory",
                    help="the directory containing txt files with data")
    parser.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Print progress")

    args = parser.parse_args(args_list)
    dirname = args.directory
    verbose = args.verbose

    print("Add your code here to do things!")


if __name__ == '__main__':
    main()
