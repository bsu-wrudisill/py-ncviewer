# import all classes/methods
# from the tkinter module


import sys
from metaread import get_varnames
from guimaker import *
import argparse


if __name__ == "__main__":
    # thefile = '/Users/william/Desktop/fastsled.level1.asfs50-picnic.20211012.000000.nc'
    # /Volumes/Transcend/sail_data/HRRR_data/t2m
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')           # positional argument
    args = parser.parse_args()
#    ds = concatenator(args.filenames)
#    thefile = '/Volumes/Transcend/sail_data/HRRR_data/t2m/hrrr_t2m_2022-01-22_0500.nc'

    print(args.filenames)

    app = App(args.filenames) 
    app.mainloop()
