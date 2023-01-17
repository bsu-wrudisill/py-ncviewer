# import all classes/methods
# from the tkinter module
import sys
from metaread import get_varnames
from guimodule import build_gui
import xarray as xr 
import matplotlib.pyplot as plt 


thefile = sys.argv[1]

buttons = get_varnames(thefile)
xrds = xr.open_dataset(thefile)

window = build_gui(buttons, xrds)

# run the gui
window.mainloop()




#if __name__ == "__main__":#
