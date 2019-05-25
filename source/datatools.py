from datetime import timedelta
import numpy as np
import pandas as pd
import sys

def load_data(filename, time_jump_min=30):
    # Get the data from the file only for the required columns.
    selected_cols = ['FLNR.1', 'SOBT', 'SIBT', 'DT', 'POSA/D']
    flights = pd.read_csv(filename)[selected_cols]

    # Filter flights other than those on 2nd May.
    flights = flights[flights['DT'] == 2]
    flights.dropna(inplace=True)

    # Convert SIBT and SOBT to datetime objects.
    flights['SIBT'] = pd.to_datetime('2019-06-02 ' + flights['SIBT'])
    flights['SOBT'] = pd.to_datetime('2019-06-02 ' + flights['SOBT'])
    flights.sort_values(['SOBT', 'SIBT'], inplace=True)

    # Filter flights with a turn-around-time of more than 30 minutes.
    flights = flights[(flights['SOBT'] - flights['SIBT']) > timedelta(minutes=time_jump_min)]

    # Split POSA/D to get the departure terminal. Remove the terminals we aren't interested in.
    flights['terminal'] = flights['POSA/D'].str.split('/', expand=True).iloc[:, 1]

    excluded = ['502', '503', '504', '505', '506', '507', '508', '509', '510']
    flights = flights[~flights['terminal'].isin(excluded)]

    # Rename FLNR column for consistency.
    flights.rename(columns={'FLNR.1': 'flight'}, inplace=True)

    # Filter flights with highest TAT when there is contention for a stand.
    flights.reset_index(drop=True, inplace=True)
    flights = filter_contention(flights)

    # Refueling time is 30 minutes prior to the flight take off time.
    flights['refuelat'] = flights['SOBT'] - timedelta(minutes=time_jump_min)
    flights.sort_values('refuelat', inplace=True)

    # Drop the columns we no longer need.
    flights.reset_index(drop=True, inplace=True)
    flights.drop(columns=selected_cols[1:], inplace=True)

    return flights


def load_distances(filename):
    distances = pd.read_csv(filename, index_col=0)
    distances['T'] = 0
    distances.loc['T'] = 0
    return distances


def filter_contention(flightinfo):
    _flightinfo = flightinfo.sort_values(['terminal', 'SOBT', 'SIBT'])

    while (True):
        drop_flnr = []

        flt1 = _flightinfo[:-1].reset_index(drop=True)
        flt2 = _flightinfo[1:].reset_index(drop=True)

        tcheck = flt1['terminal'] == flt2['terminal']
        ocheck = flt1['SOBT'] > flt2['SIBT']

        check = tcheck & ocheck
        cont1 = flt1[check]
        cont2 = flt2[check]

        ind = (cont1['SOBT'] - cont1['SIBT']) < (cont2['SOBT'] - cont2['SIBT'])
        drop_flnr += cont1.loc[ind, 'flight'].tolist() + cont2.loc[~ind, 'flight'].tolist()

        _flightinfo = _flightinfo[~_flightinfo['flight'].isin(drop_flnr)]

        if (drop_flnr):
            break

    _flightinfo.sort_values(['SOBT', 'SIBT'], inplace=True)
    return _flightinfo
