# -*- coding: utf-8 -*-
"""
Created on Sun May  3 14:31:04 2026

@author: matilda
"""

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
import glob

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

	#Replace bad data with NaN
    df[['Sea Level', 'Residual']] = df[['Sea Level','Residual']].replace(r".*[MNT]$",
								    np.nan,
									regex=True
	)

    #Set Sea Level to a float
    df['Sea Level'] = df['Sea Level'].astype(float)

    df.loc[df['Sea Level'] < -90, 'Sea Level'] = np.nan


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

    #Convert start and end from strings to datetime objects and set the end
	#point to be the end of the day on the last day.
    start_datetime = datetime.datetime.strptime(start_string, '%Y%m%d')
    end_datetime = datetime.datetime.combine(
		           datetime.datetime.strptime(end_string, '%Y%m%d'),
				   datetime.time.max
    )

	#Filtering to extract dates between the start and end
    extracted_section = data.loc[(data.index >= start_datetime) & (data.index <= end_datetime)].copy()

    sea_level_mean_section = extracted_section['Sea Level'].mean()

	#Subtracting the mean sea level from the sea level column for the section.
    extracted_section['Sea Level'] = extracted_section['Sea Level'] - sea_level_mean_section

    return extracted_section


def join_data(data1, data2):

	#Check data inputs are DataFrames.
    if not (isinstance(data1, pd.DataFrame) and isinstance(data2, pd.DataFrame)):
        raise TypeError('Both inputs must be DataFrames.')

    #Join data.
    all_data = [data1,data2]
    joined = pd.concat(all_data).sort_index()

	#Remove duplicate dates.
    joined_no_duplicates = joined[~joined.index.duplicated(keep='first')]

    #Sort dates chronologically.
    return  joined_no_duplicates

def sea_level_rise(data):

    #Remove NaN values from data.
    data_no_nan = data.dropna(subset = ['Sea Level'])

	#Convert DatetimeIndex to float values.
    float_data = mdates.date2num(data_no_nan.index)
    normalised = (float_data -float_data[0])

	#Do linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
		                                          normalised,
												  data_no_nan['Sea Level'].values
	)


    return slope, p_value


def tidal_analysis(data, constituents, start_datetime):

    #Set up constituents and initial time.
    tide = uptide.Tides(constituents)
    tide.set_initial_time(start_datetime)

	#Check timezone of initial time.
    timezone = start_datetime.tzinfo

    #If the data has no timezone attached, give it the same as start_datetime
	#If it does have a timezone attached, convert it to the same as start_datetime
    if data.index.tz is None:
        timezone_index = data.index.tz_localize(timezone)
    else:
        timezone_index = data.index.tz_convert(timezone)

    #Find amount of time passed since initial time.
    time_diff = timezone_index - start_datetime
    seconds_since_start = time_diff.total_seconds().values

    amp, pha = uptide.harmonic_analysis(tide, data['Sea Level'].values, seconds_since_start)

    return amp, pha


def get_longest_contiguous_data(data):

	#Finding the locations of NaN and create streaks between breaks.
	streaks = data['Sea Level'].isna().cumsum()

	#Remove rows with NaN values from data and from the corresponding rows in
	#streaks
	valid_data = data.dropna(subset=['Sea Level'])
	valid_streaks = streaks[data['Sea Level'].notna()]

	#Group rows by streak ID and find length of each.
	streak_length = valid_data.groupby(valid_streaks).size()

	#Find ID fof longest streak
	longest_streak_id = streak_length.idxmax()

	#Isolate data with with the longest streak ID.
	longest_data = valid_data[valid_streaks == longest_streak_id]

	return longest_data


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

    #Find pathway to wanted files.
    files = glob.glob(os.path.join(dirname, '*.txt'))

	#Read the first file
    full_data = read_tidal_data(files[0])

    #Go through files and implement read_tidal_data function to each year
    for file_path in files[1:]:
	    current_year = read_tidal_data(file_path)
	    #Adding year tables to main table
	    full_data = join_data(full_data, current_year)

	#Get cleaned version of longest streak of contiguous data
    best_data = get_longest_contiguous_data(full_data)

    #Find start datetime and set timezone to utc
    start_datetime = best_data.index[0].tz_localize('UTC')

    #Split the results up into amplitude and phase.
    amp, pha = tidal_analysis(best_data,['M2','S2'], start_datetime)

    #Use all years to get a more accurate result
    long_sea_rise = sea_level_rise(full_data)*365

    m2_amp = amp[0]
    s2_amp = amp[1]
    m2_pha = pha[0]
    s2_pha = pha[1]

    summary = f"""
	---Tidal Analysis Results---
	Sea Level Rise: {long_sea_rise} m/year
	M2 Amplitude: {m2_amp}
        M2 Phase: {m2_pha}
        S2 Amplitude: {s2_amp}
        S2 Phase: {s2_pha}
"""
    if verbose:
	    print(summary)
    else:
	    with open('results.txt','w') as f:
		    f.write(summary)

if __name__ == '__main__':
    main()
