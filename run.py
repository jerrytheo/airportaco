from source import airportaco
from os import system
from source import datatools

import numpy as np

FLIGHTS_FILE = "data/flight-schedule.csv"
DISTANCES_FILE = "data/distances.csv"
NUM_TRUCKS = 13
TRUCK_SPEED_KMPH = 20


if __name__ == '__main__':
    system('cls')

    flights = datatools.load_data(FLIGHTS_FILE)
    distances = datatools.load_distances(DISTANCES_FILE)

    # Hack to drop missing stands.
    stands1 = np.unique(flights['terminal'])
    stands2 = np.unique(distances.columns)
    flights = flights[~flights['terminal'].isin(np.setdiff1d(stands1, stands2))]

    speed_in_mpm = TRUCK_SPEED_KMPH * 1000 / 60
    optimizer = airportaco.AirportACO(flights, distances, ntrucks=13, truckspeed=speed_in_mpm)
    optimizer.run()
