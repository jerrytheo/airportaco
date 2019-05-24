from source import airportaco
from source import datatools

FLIGHTS_FILE = "data/flight-schedule.csv"
DISTANCES_FILE = "data/distances.csv"


if __name__ == '__main__':
    flights = datatools.load_data(FLIGHTS_FILE)
    distances = datatools.load_distances(DISTANCES_FILE)

    airportaco.get_schedule(flights, distances)
