# Py-NcViewer

This is a command-line application for quickly viewing netcdf files using the power of Xarray (https://docs.xarray.dev/en/stable/index.html) and Matplotlib. It is designed to emulate some of the functionality of the original "Ncview". The gui is written in "tkinter" (https://docs.python.org/3/library/tkinter.html) which is old but offers the functionality needed for this basic program. 

## Dependencies:


## Usage:
The program can take single files or multiple files as input. Wildcard expressions can be used to pass in filenames to the program. The program will try to concatenate the files together using the xr.open_mfdataset (https://docs.xarray.dev/en/stable/generated/xarray.open_mfdataset.html) command.

## Examples:

Here are some screenshots of the "beta" version, showing a 2-d field plotted:

![image](https://user-images.githubusercontent.com/11933429/222013271-f9fb8b3f-b974-48f5-bdb6-e5b83c1ed17f.png)

The code is also meant to work with timeseries data. If a datetime like object is present, then there is an option to resample the data to a different frequency.

![image](https://user-images.githubusercontent.com/11933429/222013590-fbf368fb-c5ce-44ff-8d1c-f33992e6e529.png)
