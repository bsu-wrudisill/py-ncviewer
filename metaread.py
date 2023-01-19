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


def get_dimensions(ds):
    # ds is an already opened data array or dataset 
    var4d = []
    var3d = []
    var2d = []
    var1d = []

    # loop thru them 
    for var in ds.data_vars:
        if len(ds[var].shape) == 1:
            var1d.append(var)
        if len(ds[var].shape) == 2:
            var1d.append(var)
        if len(ds[var].shape) == 3:
            var1d.append(var)
        if len(ds[var].shape) == 4:
            var1d.append(var)
            
    return {"4d":var4d,
            "3d":var3d,
            "2d":var2d,
            "1d":var1d}
    
if __name__ == "__main__":
    ds = xreader("/Volumes/Transcend/sail_data/HRRR_data/t2m/hrrr_t2m_2022-02-03_0300.nc")      
    get_dimensions(ds)