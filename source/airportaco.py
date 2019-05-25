import numpy as np
from datetime import timedelta

from .ant import AirportAnt


class AirportACO:

    def __init__(self, flightinfo, distmatrix, nants=100, ntrucks=10,
            truckspeed=100, time_to_refuel=5):

        self.flightinfo = flightinfo
        self.distmatrix = distmatrix

        self.ntrucks = ntrucks
        self.truckspeed = truckspeed
        self.time_to_refuel = time_to_refuel

        self.ants = []
        for _ in range(nants):
            self.ants.append(AirportAnt(self))

        self.global_best = 0
        self.local_updates = np.zeros(ntrucks)
        self.pheromones = np.random.rand(flightinfo.shape[0], ntrucks, ntrucks)


    def run(self, max_iter=100, stable_iter=10):
        stable_ii = 0
        status_text = 'Iter: {:02d}  Ant: {:02d}  '
        for ii in range(max_iter):
            pickers = np.random.rand(len(self.ants), self.flightinfo.shape[0])
            for ant_ii, ant in enumerate(self.ants):
                ant.update(pickers[ant_ii], status_text.format(ii, ant_ii))
                return

            # prev_best = self.global_best
            # self.local_updates = np.array([ant.update() for ant in self.ants])
            # self.global_best = np.min(self.local_updates)

            # if self.global_best == prev_best:
            #     stable_ii += 1
            #     if stable_ii == stable_iter:
            #         return


def get_schedule(flightinfo, distmatrix):
    print(flightinfo.shape)
    print(distmatrix)


def construct_weight_matrix(flightinfo, distmatrix):
    pass

def update_weight_matrix(flightinfo, weights, curtime, assignments):
    pass
