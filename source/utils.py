import numpy as np


def ceil_to_base(x, base=5):
    return base * np.ceil(x / base)


def print_output(optimizer, flights):
    print('\n\nResults')
    print('-------', end='\n\n')

    print_row = '{:>10}    {:>9}'

    print(print_row.format('FLNR', 'TRUCK_NUM'))
    print(print_row.format('----', '---------'))

    for i in range(optimizer.nflights):
        print(print_row.format(flights.iloc[i]['flight'], optimizer.gbest_path[i+1] + 1))


    print('\n\nTOTAL TIME TRAVELLED: ', optimizer.gbest_cost, end='\n\n')
