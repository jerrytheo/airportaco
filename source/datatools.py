from datetime import timedelta
import numpy as np
import pandas as pd
import sys

def load_data(filename):
    # Get the data from the file only for the required columns.
    selected_cols = ['FLNR.1', 'SOBT', 'DT', 'POSA/D']
    flights = pd.read_csv(filename)[selected_cols]

    # # Filter flights other than those on 2nd May.
    flights = flights[flights['DT'] == 2]
    flights.dropna(inplace=True)

    # Refueling time is 30 minutes prior to the flight take off time.
    flights['refuelat'] = pd.to_datetime('2019-06-02 ' + flights['SOBT']) - timedelta(minutes=30)
    flights.sort_values('refuelat', inplace=True)

    # Split POSA/D to get the departure terminal. Remove the terminals we aren't interested in.
    flights['terminal'] = flights['POSA/D'].str.split('/', expand=True).iloc[:, 1]

    excluded_cols = ['502', '503', '504', '505', '506', '507', '508', '509', '510']
    flights = flights[~flights['terminal'].isin(excluded_cols)]

    # Rename FLNR column for consistency.
    flights.rename(columns={'FLNR.1': 'flight'}, inplace=True)

    # Drop the columns we no longer need.
    flights.drop(columns=selected_cols[1:], inplace=True)

    return flights


def load_distances(filename):
    distances = pd.read_csv(filename, index_col=0)
    distances['T'] = 0
    distances.loc['T'] = 0
    return distances
