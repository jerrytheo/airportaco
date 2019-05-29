from source import airportaco
from os import system
from source import datatools

import numpy as np

FLIGHTS_FILE = "data/flight-schedule.csv"
DISTANCES_FILE = "data/distances.csv"
NUM_TRUCKS = 20
TRUCK_SPEED_KMPH = 20
BOARDING_TIME = 10
REFUELING_TIME = 5
Q_STRENGTH = 2000
NUM_ANTS = 20

if __name__ == '__main__':
    system('cls')

    flights = datatools.load_data(FLIGHTS_FILE, time_jump_min=BOARDING_TIME + REFUELING_TIME)
    distances = datatools.load_distances(DISTANCES_FILE)

    # Hack to drop missing stands.
    stands1 = np.unique(flights['terminal'])
    stands2 = np.unique(distances.columns)
    flights = flights[~flights['terminal'].isin(np.setdiff1d(stands1, stands2))]
    flights.reset_index(drop=True, inplace=True)

    speed_in_mpm = TRUCK_SPEED_KMPH * 1000 / 60
    optimizer = airportaco.AirportACO(flights, distances, nants=NUM_ANTS, qstr=Q_STRENGTH,
        ntrucks=NUM_TRUCKS, truckspeed=speed_in_mpm, time_to_refuel=REFUELING_TIME)
    optimizer.run()
    print(optimizer.gbest_path)
    print(optimizer.gbest_cost)
