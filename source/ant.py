import datetime as dt
import numpy as np

from .utils import ceil_to_base
import sys


class AirportAnt:

    def __init__(self, colony):
        self.colony = colony

        self.current_schedule   = []
        self.truck_assignments  = np.repeat('P', self.colony.ntrucks)
        self.truck_intransit    = np.zeros(self.colony.ntrucks, dtype=np.timedelta64)
        self.assignment_times   = np.repeat(
            np.datetime64(colony.flightinfo.iloc[0, :]['refuelat']) - np.timedelta64(1, 'D'), self.colony.ntrucks)
        self.prev_assignment    = 0


    def update(self, picker):

        for flt_ii, flight in self.colony.flightinfo.iterrows():
            print('Flight: {}'.format(flight['flight']))

            refuelat = np.datetime64(flight['refuelat'])

            eta = self.get_weights(refuelat, flight['terminal'])
            tau = self.colony.pheromones[flt_ii, self.prev_assignment]

            term = eta * tau
            cfrq = np.cumsum(term / np.sum(term))

            print(flight)
            self.assign_truck(np.argmax(picker < cfrq), flight['refuelat'], flight['terminal'])


    def get_weights(self, reftime, destterm):
        time_to_dest = self.get_time_to_dest(self.truck_assignments, destterm, cast=False)
        availability = self.get_truck_availability(reftime, time_to_dest)

        return (1 / time_to_dest) * availability


    def get_truck_availability(self, reftime, time_to_dest):
        assigned_p = self.truck_assignments == 'P'                              # Trucks assigned to parking.
        ready_time = reftime - time_to_dest.astype('timedelta64[m]')            # Time to get ready for heading out.

        reach_time = self.assignment_times + self.truck_intransit               # Time the truck reaches its destination.
        done_time = reach_time + self.colony.time_to_refuel                     # Time the truck completes refueling.

        # Is at parking on or before its time_to_dest. No updates needed.
        idle_trucks = assigned_p & (reach_time <= ready_time)

        # Is assigned but completes exactly time_to_dest before.
        done_trucks = ~assigned_p & (done_time == ready_time)

        # Is assigned, completes and reaches 'P' before time_to_dest.
        time_to_getback = self.get_time_to_dest(self.truck_assignments,'P')
        overacheivers   = ~assigned_p & ((done_time + time_to_getback) < reftime)

        return idle_trucks | done_trucks | overacheivers


    def assign_truck(self, ind, reftime, destterm):
        self.current_schedule.append(ind)

        self.update_trucks(ind, reftime, destterm)
        self.update_availability(reftime, destterm)


    def update_trucks(self, index, atime, destn):
        self.assignment_times[index] = atime
        self.truck_intransit[index] = self.get_time_to_dest(self.truck_assignments[index], destn)
        self.truck_assignments[index] = destn


    def update_availability(self, reftime, destterm):
        ready_time = reftime - self.get_time_to_dest(self.truck_assignments, destterm)

        # Update trucks that complete early.
        done_time = self.assignment_times + self.truck_intransit + self.colony.time_to_refuel
        trucks_done = (self.truck_assignments != 'P') & (done_time < ready_time)
        self.update_trucks(trucks_done, done_time[trucks_done], 'P')

        # Update trucks that reach parking early.
        reach_time = self.assignment_times + self.truck_intransit
        trucks_reached = (self.truck_assignments == 'P') & (reach_time < ready_time)

        self.truck_intransit[trucks_reached] = np.timedelta64(0, 'm')
        self.assignment_times[trucks_reached] = reach_time[trucks_reached]


    def get_time_to_dest(self, sources, destinations, cast=True):
        distances = self.colony.distmatrix.loc[sources, destinations]
        if distances.ndim > 0:
            distances = distances.values
        time_to_dest = ceil_to_base(distances / self.colony.truckspeed)

        if cast:
            time_to_dest = time_to_dest.astype('timedelta64[m]')

        return time_to_dest
