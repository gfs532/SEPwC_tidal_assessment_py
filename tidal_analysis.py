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
    """Input - file from user
    Function - read and do preliminary formatting of file.
    """

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

	#Set the index to the datetime column
    df = df.set_index('date_and_time')

	#Remove repeat columns.
    df = df.drop(columns=['Date','Time'])

	#Replace bad data with NaN
    df[['Sea Level', 'Residual']] = df[['Sea Level','Residual']].replace(r".*[MNT]$",
								    np.nan,
									regex=True
	)

    #Set Sea Level to a float
    df['Sea Level'] = df['Sea Level'].astype(float)


    return df


def extract_single_year_remove_mean(year, data):

	#Extract the data for a single year.
    single_year_data = data.loc[str(year)].copy()

    sea_level_mean = single_year_data['Sea Level'].mean()

	#Subtracting the mean sea level from the sea level column for the single year.
    single_year_data['Sea Level'] = single_year_data['Sea Level'] - sea_level_mean


    return single_year_data


def extract_section_remove_mean(start, end, data):

	#Convert start and end from integers to strings to use with datetime.
    start_string = str(start)
    end_string = str(end)

    #Convert start and end from strings to datetime objects.
    start_datetime = datetime.datetime.strptime(start_string, '%Y%m%d')
    end_datetime = datetime.datetime.strptime(end_string, '%Y%m%d')

	#Filtering to extract dates between the start and end
    extracted_section = data.loc[(data.index >= start_datetime) & (data.index <= end_datetime)].copy()

    sea_level_mean_section = extracted_section['Sea Level'].mean()

	#Subtracting the mean sea level from the sea level column for the section.
    extracted_section['Sea Level'] = extracted_section['Sea Level'] - sea_level_mean_section

    return extracted_section


def join_data(data1, data2):

	#Check data inputs are DataFrames.
    if not isinstance(data1, pd.DataFrame):
        raise TypeError('Both inputs must be DataFrames.')

    #Join data.
    all_data = [data1,data2]
    joined = pd.concat(all_data)

	#Remove duplicate dates.
    joined_no_duplicates = joined.drop_duplicates(
                           subset=joined.index,
		                   keep='first'
   )

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
