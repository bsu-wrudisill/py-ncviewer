import xarray as xr 
import argparse

def get_varnames(flist):
    if type(flist) == list:
        ds = xr.open_dataset(flist[0]) # get only one of the files...

    if type(flist) == str:
        ds = xr.open_dataset(flist) # get only one of the files...

    return list(ds.data_vars), list(ds.coords)
    ds.close()


def xreader(thefile):
    if len(thefile) == 1:
        # 'thefile' will be a list, and open_dataset needs a string
        return xr.open_dataset(thefile[0],engine="netcdf4")

    else:
        return xr.open_mfdataset(thefile, 
                                 engine="netcdf4", 
                                 combine="by_coords", 
                                 parallel=True)

    
if __name__ == "__main__":
    pass