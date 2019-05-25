import datetime as dt
import numpy as np

from .utils import ceil_to_base
import sys


class AirportAnt:

    def __init__(self, colony):
        self.colony = colony

        self.current_schedule   = []
        self.truck_assignments  = np.array(['P'] * self.colony.ntrucks, dtype=object)
        self.truck_intransit    = np.zeros(self.colony.ntrucks, dtype='timedelta64[m]')
        self.assignment_times   = np.repeat(
            np.datetime64(colony.flightinfo.iloc[0, :]['refuelat']) - np.timedelta64(1, 'D'), self.colony.ntrucks)
        self.prev_assignment    = 0
        self.total_distance     = 0


    def update(self, picker, prefix_log=''):

        for flt_ii, flight in self.colony.flightinfo.iterrows():
            refuelat = np.datetime64(flight['refuelat'])

            eta = self.get_weights(refuelat, flight['terminal'])
            tau = self.colony.pheromones[flt_ii, self.prev_assignment]

            term = eta * tau
            cfrq = np.cumsum(term / np.sum(term))

            truck_index = np.argmax(picker[flt_ii] < cfrq)                  # Randomly select a truck by cum. freq.
            self.current_schedule.append(truck_index)

            self.update_trucks(truck_index, refuelat, flight['terminal'])   # Update the assigned truck.
            self.update_availability(refuelat, flight['terminal'])          # Update the other trucks.

            array_display = ('{:>4}' * 13).format(*self.truck_assignments)
            print(prefix_log + 'Flight: {:10}  {}'.format(flight['flight'], array_display))


    def get_weights(self, reftime, destterm):
        time_to_dest = self.get_time_to_dest(self.truck_assignments, destterm)
        availability = self.get_truck_availability(reftime, time_to_dest)

        if np.any(time_to_dest.astype('float') == 0):
            print(reftime, self.truck_assignments, destterm)
            sys.exit()
        return (1 / time_to_dest.astype('float')) * availability


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


    def update_trucks(self, index, atime, destn):
        time_to_dest = self.get_time_to_dest(self.truck_assignments[index], destn)
        self.truck_intransit[index] = time_to_dest[0] if time_to_dest.shape[0] == 1 else time_to_dest

        self.assignment_times[index] = atime
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


    def get_time_to_dest(self, sources, destinations):
        distances = np.atleast_1d(self.colony.distmatrix.loc[sources, destinations])
        time_to_dest = ceil_to_base(distances / self.colony.truckspeed).astype('timedelta64[m]')

        return time_to_dest
