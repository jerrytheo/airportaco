import numpy as np
from datetime import timedelta

from .ant import AirportAnt


class AirportACO:

    def __init__(self, flightinfo, distmatrix, nants=10, evrate=0.3, qstr=1,
            ntrucks=10, truckspeed=100, time_to_refuel=5):

        self.flightinfo = flightinfo
        self.distmatrix = distmatrix

        self.evrate         = evrate
        self.qstrength      = qstr
        self.ntrucks        = ntrucks
        self.truckspeed     = truckspeed
        self.time_to_refuel = time_to_refuel

        self.ants = []
        for _ in range(nants):
            self.ants.append(AirportAnt(self))

        nflights = flightinfo.shape[0]
        self.gbest_cost = 5000
        self.gbest_path = np.zeros(nflights)
        self.pheromones = np.random.rand(nflights, ntrucks, ntrucks)

    def run(self, max_iter=500, stable_iter=100):
        result = self._run(max_iter, stable_iter)
        print('')
        return result

    def _run(self, max_iter=500, stable_iter=100):
        stable_ii = 0
        status_text = 'Iter: {:02d}  Ant: {:02d}  '

        for ii in range(max_iter):
            # Random pickers for sampling.
            pickers = np.random.rand(len(self.ants), self.flightinfo.shape[0])

            for ant_ii, ant in enumerate(self.ants):

                prev_best = self.gbest_cost

                # Update the ant.
                ant.update(pickers[ant_ii], status_text.format(ii, ant_ii))

                # Update global best.
                if ant.total_time < self.gbest_cost:
                    self.gbest_cost = ant.total_time
                    self.gbest_path[:] = ant.current_schedule

                self.update_pheromones(ant.current_schedule, ant.total_time)

                if self.gbest_cost == prev_best:
                    print(self.gbest_cost)
                    stable_ii += 1
                    if stable_ii == stable_iter:
                        return True
                else:
                    stable_ii = 0

        return False


    def update_pheromones(self, path, cost):
        self.pheromones *= (1 - self.evrate)

        # Pheromones to update.
        ind = np.array([
            np.arange(1, self.pheromones.shape[0]),
            path[:-1],
            path[1:]], dtype=int)

        self.pheromones[ind[0], ind[1], ind[2]] += self.qstrength / cost