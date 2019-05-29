import numpy as np
from datetime import timedelta
import sys

from .ant import AirportAnt


class AirportACO:

    def __init__(self, flightinfo, distmatrix, nants=10, evrate=0.3, qstr=1,
                 ntrucks=10, truckspeed=100, time_to_refuel=5):

        # Datasets.
        self.flightinfo     = flightinfo
        self.distmatrix     = distmatrix
        self.nflights       = flightinfo.shape[0]

        # ACO parameters.
        self.evrate         = evrate        # Evaporation rate.
        self.qstrength      = qstr          # Pheromone addition rate.

        # Airport assumptions.
        self.ntrucks        = ntrucks
        self.truckspeed     = truckspeed
        self.time_to_refuel = time_to_refuel

        # Initialize the ants.
        self.ants = []
        for _ in range(nants):
            self.ants.append(AirportAnt(self))


        # Initialize the global best values.
        # (Assuming total time cannot take more than 5000 minutes.)
        self.gbest_cost = 5000.0
        self.gbest_path = np.zeros(self.nflights)

        # Initialize pheromones.
        self.pheromones = np.random.rand(self.nflights, ntrucks, ntrucks)
        self.pheromones[0, 1:] = 0

        # Track the paths taken by the ants and their costs over each iteration.
        self.ant_paths = np.zeros((nants, self.nflights + 1), dtype=int)
        self.ant_costs = np.zeros(nants)

    def run(self, max_iter=100, stable_iter=10):

        # Check stability.
        stable_ii = stable_iter

        # Text to display.
        status_text = 'Iter: {:02d}  Best: {:04.0f}  Ant: {:02d}  '

        for ii in range(max_iter):

            # Random pickers for sampling.
            pickers = np.random.rand(len(self.ants), self.flightinfo.shape[0])

            # Save previous best to check stability.
            prev_best = self.gbest_cost
            print(prev_best, end='\r')

            # Update each ant.
            for ant_ii, ant in enumerate(self.ants):
                ant.generate_schedule(
                    pickers[ant_ii], status_text.format(ii, self.gbest_cost, ant_ii))
                self.ant_costs[ant_ii] = ant.total_time
                self.ant_paths[ant_ii, 1:] = ant.current_schedule

            # Update the global best solution if it changes.
            lbest_cost = np.min(self.ant_costs)
            if lbest_cost < self.gbest_cost:
                self.gbest_cost = lbest_cost
                self.gbest_path = self.ant_paths[np.argmin(self.ant_costs)].copy()

            self.update_pheromones()

            # Check if the solution has remained stable.
            if self.gbest_cost == prev_best:
                stable_ii -= 1
                if not stable_ii:
                    print('')
                    return True
            else:
                stable_ii = stable_iter

            print('')

        return False


    def update_pheromones(self):

        # Decrease pheromones by evaporation rate.
        self.pheromones *= (1 - self.evrate)

        flight_ind = np.arange(self.nflights)           # Update each flight once.
        prev_truck = self.ant_paths[:, :-1]             # Truck assigned to previous flight.
        curr_truck = self.ant_paths[:, 1:]              # Truck assigned to current flight.
        edges = np.dstack((prev_truck, curr_truck))     # Graph edges.

        for i in range(len(self.ants)):
            v1 = edges[i, :, 0]                         # Edge starting vertex.
            v2 = edges[i, :, 1]                         # Edge ending vertex.
            self.pheromones[flight_ind, v1, v2] += self.qstrength / self.ant_costs[i]
