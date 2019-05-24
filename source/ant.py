import datetime as dt
import numpy as np

from .utils import ceil_to_base


class AirportAnt:

    def __init__(self, starttime, distances, ntrucks=10, truckspeed=15, time_to_refuel=20):
        self.distances          = distances
        self.ntrucks            = ntrucks
        self.truckspeed         = truckspeed
        self.time_to_refuel     = time_to_refuel
        self.current_schedule   = []
        self.truck_assignments  = np.repeat('P', self.ntrucks)
        self.truck_intransit    = np.zeros(self.ntrucks, dtype=np.timedelta64)
        self.assignment_times   = np.repeat(starttime, self.ntrucks)


    def get_weights(self, reftime, destterm):
        time_to_dest = self.get_time_to_dest(self.truck_assignments, destterm, cast=False)
        availability = self.get_truck_availability(reftime, time_to_dest)

        return (1 / time_to_dest) * availability


    def get_truck_availability(self, reftime, time_to_dest):
        assigned_p = self.truck_assignments == 'P'                              # Trucks assigned to parking.
        ready_time = reftime - time_to_dest.astype('timedelta64[m]')            # Time to get ready for heading out.
        reach_time = self.assignment_times + self.truck_intransit               # Time the truck reaches its destination.
        done_time = reach_time + self.time_to_refuel                            # Time the truck completes refueling.

        # Is at parking on or before its time_to_dest. No updates needed.
        idle_trucks = assigned_p & (reach_time <= ready_time)

        # Is assigned but completes exactly time_to_dest before.
        done_trucks = ~assigned_p & (done_time == ready_time)

        # Is assigned, completes and reaches 'P' before time_to_dest.
        time_to_getback = self.get_time_to_dest(self.truck_assignments,'P')
        overacheivers   = ~assigned_p & ((done_time + time_to_getback) < reftime)

        return idle_trucks & done_trucks & overacheivers


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
        done_time = self.assignment_times + self.truck_intransit + self.time_to_refuel
        trucks_done = (self.truck_assignments != 'P') & (done_time < ready_time)
        self.update_trucks(trucks_done, done_time[trucks_done], 'P')

        # Update trucks that reach parking early.
        reach_time = self.assignment_times + self.truck_intransit
        trucks_reached = (self.truck_assignments == 'P') & (reach_time < ready_time)

        self.truck_intransit[trucks_reached] = np.timedelta64(0, 'm')
        self.assignment_times[trucks_reached] = reach_time[trucks_reached]


    def get_time_to_dest(self, sources, destinations, cast=True):
        time_to_dest = ceil_to_base(self.distances.loc[sources, destinations].values / self.truckspeed)
        if cast:
            time_to_dest = time_to_dest.astype('timedelta64[m]')
        return time_to_dest