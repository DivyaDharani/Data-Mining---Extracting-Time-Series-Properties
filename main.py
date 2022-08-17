#!/usr/bin/env python
# coding: utf-8

# # Project 1: Extracting Time Series Properties of Glucose Levels in Artificial Pancreas Purpose

import pandas as pd
import datetime as dt
import time
import math

# ### CGM (Continuous Glucose Monitor) and Insulin Datasets

insulin_data_set_full = pd.read_csv('InsulinData.csv')
insulin_data = insulin_data_set_full[['Date', 'Time', 'Alarm']]
cgm_data_set_full = pd.read_csv('CGMData.csv')
cgm_data = cgm_data_set_full[['Date', 'Time', 'Sensor Glucose (mg/dL)']]

# ### Combining Date and Time as DateTime object

insulin_data['DateTime'] = pd.to_datetime(insulin_data['Date'] + " " + insulin_data['Time'], format = '%m/%d/%Y %H:%M:%S')

cgm_data['DateTime'] = pd.to_datetime(cgm_data['Date'] + " " + cgm_data['Time'], format = '%m/%d/%Y %H:%M:%S')


# ### Finding when the auto mode is turned on based on the earliest 'AUTO MODE ACTIVE PLGM OFF' alarm code

auto_mode_start_datetime = insulin_data[insulin_data['Alarm'] == 'AUTO MODE ACTIVE PLGM OFF']['DateTime'].min()


# ### Splitting the CGM data based on auto and manual modes

cgmAutoDf = cgm_data[cgm_data['DateTime'] >= auto_mode_start_datetime]

cgmManualDf = cgm_data[cgm_data['DateTime'] < auto_mode_start_datetime]

# ### Dividing the CGM data into different timeframes - day time and night time

cgmAutoDayDf = cgmAutoDf[cgmAutoDf['DateTime'].dt.hour >= 6]

cgmAutoNightDf = cgmAutoDf[cgmAutoDf['DateTime'].dt.hour < 6]

cgmManualDayDf = cgmManualDf[cgmManualDf['DateTime'].dt.hour >= 6]

cgmManualNightDf = cgmManualDf[cgmManualDf['DateTime'].dt.hour < 6]

# ### Handling NaN values

# #### Removing the dates for which entries are not more than 70% of the expected count

def drop_dates_in_df(df, countCol, threshold = 0, expected_count = 288):
    groupedDataCount = df.groupby('Date').count()[countCol]
    keys_to_drop = list(groupedDataCount[(groupedDataCount / expected_count) < threshold].keys())
    result = df[~df['Date'].isin(keys_to_drop)]
    return result

threshold = 0 #not removing any data for now

#Whole day => 24 hours 
#Frequency of entries => every 5 minutes
#Entry count in 24 hours => Count of 5 minutes in a day => 288

autoModeDf = drop_dates_in_df(df = cgmAutoDf, countCol = 'Sensor Glucose (mg/dL)', threshold = threshold, expected_count = 288)

manualModeDf = drop_dates_in_df(df = cgmManualDf, countCol = 'Sensor Glucose (mg/dL)', threshold = threshold, expected_count = 288)

#Day Time => 6am to 11:59pm (18 hours)
#Frequency of entries => every 5 minutes
#Entry count per day in day time alone => Count of 5 minutes in 18 hours => 216

autoModeDayDf = drop_dates_in_df(df = cgmAutoDayDf, countCol = 'Sensor Glucose (mg/dL)', threshold = threshold, expected_count = 216)

manualModeDayDf = drop_dates_in_df(df = cgmManualDayDf, countCol = 'Sensor Glucose (mg/dL)', threshold = threshold, expected_count = 216)

#Night Time => 12am to 5:59am (6 hours)
#Frequency of entries => every 5 minutes
#Entry count per day in night time alone => Count of 5 minutes in 6 hours => 72

autoModeNightDf = drop_dates_in_df(df = cgmAutoNightDf, countCol = 'Sensor Glucose (mg/dL)', threshold = threshold, expected_count = 72)

manualModeNightDf = drop_dates_in_df(df = cgmManualNightDf, countCol = 'Sensor Glucose (mg/dL)', threshold = threshold, expected_count = 72)

# ### Interpolation


"""
autoModeDf = autoModeDf.interpolate()
manualModeDf = manualModeDf.interpolate()
autoModeDayDf = autoModeDayDf.interpolate()
manualModeDayDf = manualModeDayDf.interpolate()
autoModeNightDf = autoModeNightDf.interpolate()
manualModeNightDf = manualModeNightDf.interpolate()
"""


# ### Metrics to be extracted:
# a) Percentage time in hyperglycemia (CGM > 180 mg/dL),
# 
# b) percentage of time in hyperglycemia critical (CGM > 250 mg/dL),
# 
# c) percentage time in range (CGM >= 70 mg/dL and CGM <= 180 mg/dL),
# 
# d) percentage time in range secondary (CGM >= 70 mg/dL and CGM <= 150 mg/dL),
# 
# e) percentage time in hypoglycemia level 1 (CGM < 70 mg/dL), and
# 
# f) percentage time in hypoglycemia level 2 (CGM < 54 mg/dL).
# 
# Each of the above mentioned metrics are extracted in three different time intervals: daytime (6 am to
# midnight), overnight (midnight to 6 am) and whole day (12 am to 12 am).

def get_percentage_of_entries_within_range(dataframe, columnName, interval, expected_count_per_day):
    df = dataframe
    numDays = len(df['Date'].unique())
    outOf = numDays * expected_count_per_day
    range_entries = 0
    (minRange, maxRange) = interval
    if minRange is not None and maxRange is not None:
        range_entries = df[(df[columnName] >= minRange) & (df[columnName] <= maxRange)].count()[columnName]
    elif minRange is not None:
        range_entries = df[df[columnName] > minRange].count()[columnName]
    elif maxRange is not None:
        range_entries = df[df[columnName] < maxRange].count()[columnName]
    return (range_entries / (outOf * 1.0)) * 100

columnName = 'Sensor Glucose (mg/dL)'

manualModeDfList = [(manualModeNightDf, 288), (manualModeDayDf, 288), (manualModeDf, 288)]
autoModeDfList = [(autoModeNightDf, 288), (autoModeDayDf, 288), (autoModeDf, 288)] 

intervalList = [(180, None), (250, None), (70, 180), (70, 150), (None, 70), (None, 54)]

manualModeEntries = []
for df,expected_count_per_day in manualModeDfList:
    for interval in intervalList:
        manualModeEntries.append(get_percentage_of_entries_within_range(df, columnName, interval, expected_count_per_day))
autoModeEntries = []
for df,expected_count_per_day in autoModeDfList:
    for interval in intervalList:
        autoModeEntries.append(get_percentage_of_entries_within_range(df, columnName, interval, expected_count_per_day))
manualModeEntries.append(1.1)
autoModeEntries.append(1.1)

result_df = pd.DataFrame([manualModeEntries, autoModeEntries])

result_df.to_csv('Results.csv', index = False, header = False)
