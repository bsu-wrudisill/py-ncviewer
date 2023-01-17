import xarray as xr 


def get_varnames(path):
    ds = xr.open_dataset(path)
    return list(ds.data_vars)
    ds.close()



if __name__ == "__main__":
    thefile = '/Users/william/Desktop/fastsled.level1.asfs50-picnic.20211012.000000.nc'
    print(get_varnames(thefile))