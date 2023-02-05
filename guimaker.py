from tkinter import *
import tkinter as tk
from tkinter import ttk
import customtkinter

from metaread import get_varnames, xreader, get_dimensions

import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
#from matplotlib.figure import Figure


window_width = 1800
window_height = 2500
plt.style.use('dark_background')


class Scrollable(tk.Frame):
    """
       Make a frame scrollable with scrollbar on the right.
       After adding or removing widgets to the scrollable frame,
       call the update() method to refresh the scrollable area.
    """

    def __init__(self, frame):
        # make the scrollbar thing 
        scrollbar = tk.Scrollbar(frame, width=20, bg='black')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)# expand=True)

        # create hte canvase and add scrolling command 
        self.canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set, width=150) # WE HAVE TO SET THIS MANUALLY!!!!
        self.canvas.pack(expand=True)
        scrollbar.config(command=self.canvas.yview)
        self.canvas.bind('<Configure>', self.__fill_canvas)

        # # base class initialization
        tk.Frame.__init__(self, frame)

        # # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0, 0, window=self)#, anchor=tk.NW)
        self.canvas.bind_all('<MouseWheel>', lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

    def __fill_canvas(self, event):
        "Enlarge the windows item to the canvas width"
        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width=canvas_width)

    def update(self):
        "Update the canvas and the scrollregion"
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))
        # print("update")

class MoveButtoner(tk.Frame):
    def __init__(self, frame):
        super().__init__()#K*args, **kwargs)
        self.thetime = tk.IntVar()
        self.thetime.set(0)

        _cmd_nxt = lambda x=1 : self.move_timestep(x)
        _cmd_prv = lambda x=-1 : self.move_timestep(x)

        self.next = tk.Button(frame, text='Next', command=_cmd_nxt,  width=10)
        self.prev = tk.Button(frame, text='Prev', command=_cmd_prv,  width=10)
        self.uupp = tk.Button(frame, text='Up',   command=_cmd_nxt,  width=10)
        self.down = tk.Button(frame, text='Down', command=_cmd_prv,  width=10)

        self.next.pack(side=tk.LEFT)#grid(row=0, column=0)
        self.prev.pack(side=tk.LEFT)#grid(row=0, column=1)
        self.uupp.pack(side=tk.LEFT)#grid(row=0, column=2)
        self.down.pack(side=tk.LEFT)#grid(row=0, column=3)

    def move_timestep(self,x):    
       newtime = x + self.thetime.get()
       self.thetime.set(newtime)

class ResampleButton(tk.Frame):
    def __init__(self, frame):
        super().__init__()#K*args, **kwargs)
        mb = tk.Menubutton(frame, text="Resample", width=10)
        mb.pack(side=tk.LEFT)
        mb.menu =  Menu(mb, tearoff = 0)
        mb["menu"] =  mb.menu

        resample_freq = tk.Variable()
        resample_freq.set('-9999')

        mb.menu.add_checkbutton (label="1h",
                                 command = lambda: resample_freq.set('1h'))

        mb.menu.add_checkbutton (label="12h",
                                 command = lambda: resample_freq.set('3h'))

        mb.menu.add_checkbutton (label="24h",
                                 command = lambda: resample_freq.set('24h'))

        mb.menu.add_checkbutton (label="1w",
                                 command = lambda: resample_freq.set('1w'))

        mb.pack()

        self.resample_freq = resample_freq


class StatsButton(tk.Frame):
    def __init__(self, frame):
        super().__init__()#K*args, **kwargs)
        mb = tk.Menubutton(frame, text="Resample", width=10)
        mb.pack(side=tk.LEFT)
        mb.menu =  Menu(mb, tearoff = 0)
        mb["menu"] =  mb.menu

        mayoVar = IntVar()
        ketchVar = IntVar()

        mb.menu.add_checkbutton (label="mayo",
                                 variable=mayoVar)

        mb.menu.add_checkbutton (label="ketchup",
                                 variable=ketchVar )

        mb.pack()

class MplMaker(tk.Frame):

    def __init__(self, frame):
        # build the matplotlib grid
        self.fig  = plt.figure(constrained_layout=True)
        spec      = self.fig.add_gridspec(ncols=2, nrows=2, width_ratios=(20,1), height_ratios=(4,1))
        self.ax     = self.fig.add_subplot(spec[0,0])
        self.cbax   = self.fig.add_subplot(spec[0,1])       
        self.histax = self.fig.add_subplot(spec[1,0])       
        self.canvas = FigureCanvasTkAgg(self.fig, frame)

    def __call__(self, frame):
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(column=3, row=2, columnspan=2, rowspan=2, sticky=(N,S,E,W))
#        self.toolbar = NavigationToolbar2Tk(self.canvas, frame)
#        self.toolbar.update()
#        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.grid(row=2, column=3, columnspan=2, rowspan=2, sticky=(N,S,E,W))
        self.canvas._tkcanvas.columnconfigure(3, weight=3)
        self.canvas._tkcanvas.columnconfigure(4, weight=3)


class ButtonMaker(tk.Frame):
    def __init__(self, 
                 *args, 
                 xrds=None,
                 column_title=None,
                 buttons=None,
                 header_name=None, 
                 canvasobject=None,
                 clicked_button=None,
                 move_buttons=None,
                 resample_buttons=None,
                 **kwargs):

        super().__init__(*args, **kwargs)
        self.xrds = xrds 
        self.clicked_button = clicked_button
        self.canvasobject = canvasobject
#        self.original_size = canvasobject.fig.get_size_inches()
        self.move_buttons = move_buttons
        self.resample_buttons = resample_buttons
        # go through each varianble and make a button
        for i, button in enumerate(buttons):   
            _cmd = lambda x=button: self.button_event(x)

            self.button_x = tk.Button(self, text=str(button), command=_cmd, width=60)#, highlightbackground='black')
            self.button_x.pack(padx=10,pady=2)#side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        

    def button_event(self, x):
        # get the value of the previous and next buttons
        # clear the existing canvas...
        #if len(self.canvasobject.fig.axes) > 1:
        #    self.canvasobject.fig.axes[1].remove()
            #reset_axsize(self.original_size[1], self.original_size[0], self.canvasobject.ax)

        # get the variable 
        plotting_variable = self.xrds.get(x) #.isel()#time=self.move_buttons.thetime.get())

        # get the variable attributed and pass it along ...
        pv_attrs_str = ["%s : %s"%(x, plotting_variable.attrs[x]) for x in plotting_variable.attrs.keys()]
        pv_attrs_str = "\n".join(pv_attrs_str)
        self.clicked_button.set(pv_attrs_str)

        for axx in [self.canvasobject.ax, 
                    self.canvasobject.cbax, 
                    self.canvasobject.histax]:

            axx.clear()

        # MOVE THIS SOMEWHERE ELSE SO THAT IT DOESNT HAPPEN EVERY CLICK
        one_len_list = {}
        for i,k in enumerate(plotting_variable.shape):
            if k == 1:
                one_len_list[plotting_variable.dims[i]] = 0

        # just go ahead and select these -- makes dim size smaller 
        plotting_variable = plotting_variable.sel(**one_len_list)
                
        # select the concat dim if it's in there. ..
        if len(plotting_variable.shape) > 1:

            if "CONCAT_DIM" in list(plotting_variable.dims):
                plotting_variable = plotting_variable.isel(CONCAT_DIM=self.move_buttons.thetime.get())

            if "Time" in list(plotting_variable.dims):
                plotting_variable = plotting_variable.isel(Time=self.move_buttons.thetime.get())

            if "time" in list(plotting_variable.dims):
                plotting_variable = plotting_variable.isel(time=self.move_buttons.thetime.get())

            if "XTIME" in list(plotting_variable.dims):
                plotting_variable = plotting_variable.isel(XTIME=self.move_buttons.thetime.get())

            if "date" in list(plotting_variable.dims):
                plotting_variable = plotting_variable.isel(date=self.move_buttons.thetime.get())

        # othersiwse, don't select anything .... 
        # get some info about the plotting variable ...        
        if len(plotting_variable.shape) > 5:
            pass

        if len(plotting_variable.shape) == 4:
            pass 

        if len(plotting_variable.shape) == 3:
            pass 
   
        if len(plotting_variable.shape) == 2: 
            a = plotting_variable.plot(ax=self.canvasobject.ax, 
                                       add_colorbar=False)
            # add the colorbar 
            self.canvasobject.fig.colorbar(a, cax=self.canvasobject.cbax)

            # make a histogram
            plotting_variable.plot.hist(bins=100, ax=self.canvasobject.histax)

            # plot the data...
            self.canvasobject.canvas.draw()

        if len(plotting_variable.shape) == 1: 
            # resample if necessary ...
            resample_freq = self.resample_buttons.resample_freq.get()

            if resample_freq == '-9999':
                print('first')
                plotting_variable.plot(ax=self.canvasobject.ax)
            else:
                print(resample_freq)
                plotting_variable.resample(time=resample_freq).mean().plot(ax=self.canvasobject.ax)

            # make a histogram
            plotting_variable.plot.hist(bins=100, ax=self.canvasobject.histax)

            self.canvasobject.canvas.draw()



class App(Tk):

    def __init__(self, thefile):
        super().__init__()
        ipadding = {'ipadx': 1, 'ipady': .1}

        self.configure(bg='black')
        self.clicked_button = tk.Variable(self)
        self.clicked_button.set("test")

        # make the screen show up so it is centered on the screen 
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        # set the position of the window to the center of the screen
#        self.geometry(f'{window_width*.5}x{window_height*.5}+{center_x}+{center_y}')
        self.thefile=thefile
       
        # read in the xarray stuff and make the buttons 
        datavars, coords = get_varnames(thefile)
        xrds = xreader(thefile) 
        dimensions = get_dimensions(xrds)
        mapper_frame = tk.Frame(self)

        # MAKE HTE MAP FRAME THING
        mapper_frame.grid(column=2, row=2, columnspan=6, rowspan=4)
        mapper = MplMaker(mapper_frame)

        # Label across the entire top of the frame 
        if type(thefile) == list:
            headerlabel = ".".join(thefile[0].split(".")[0:-1])+"*"
        else:
            headerlabel = thefile

        #### very top of the frame, list the name of the files being read 
        label1 = tk.Label(self,text=headerlabel, bg="green", fg="white")
        label1.grid(column=0, row=0, columnspan=8, sticky=(N, S, E, W)) 

        # have the next and up/down buttons here. second row spanning the whole thing 
        frame00 = tk.Frame(self)
        frame00.grid(column=0, row=1, columnspan=8, sticky=(N, S, E, W)) 
        move_buttons = MoveButtoner(frame00)

        # add this guy...
        resp_buttons = ResampleButton(frame00)

        # make a big box for labelling stuff before the .... thign 
        # label4 = tk.Label(self, text='test', bg="purple")
        # label4.grid(column=0, row=3, columnspan=3, rowspan=2, sticky=(N, S, E, W))


        # 4d variables 
        lbl = tk.Label(self, text="4dVar", bg='yellow', borderwidth=3, relief="raised", fg="black")
        lbl.grid(column=0, row=2, sticky=(E, W))
        frame4 = tk.Frame(self)
        frame4.grid(column=0, row=3)#, sticky=(N, S, E, W))
        scrollable_body4 = Scrollable(frame4)
        self.button_frame_4 = ButtonMaker(scrollable_body4,
                                          column_title='4dVars',
                                          buttons=dimensions['4d'], 
                                          xrds=xrds,
                                          canvasobject=mapper,
                                          clicked_button=self.clicked_button,
                                          move_buttons=move_buttons,
                                          resample_buttons=resp_buttons)


        self.button_frame_4.pack(fill=tk.Y)
        scrollable_body4.update()


        # 3d variables 
        lbl = tk.Label(self, text="3dVar", bg='yellow', borderwidth=3, relief="raised", fg="black")
        lbl.grid(column=1, row=2, sticky=(E, W))
        frame3 = tk.Frame(self)
        frame3.grid(column=1, row=3)#, sticky=(N, S, E, W))
        scrollable_body3 = Scrollable(frame3)
        self.button_frame_3 = ButtonMaker(scrollable_body3,
                                            column_title='3dVars',
                                            buttons=dimensions['3d'], 
                                            xrds=xrds,
                                            clicked_button=self.clicked_button,
                                            canvasobject=mapper,
                                            move_buttons=move_buttons,
                                            resample_buttons=resp_buttons)

        self.button_frame_3.pack()
        scrollable_body3.update()


        # 2d variables 
        lbl = tk.Label(self, text="2dVar", bg='yellow', borderwidth=3, relief="raised", fg="black")
        lbl.grid(column=0, row=4, sticky=(E, W))
        frame2 = tk.Frame(self)
        frame2.grid(column=0, row=5)#, sticky=(N, S, E, W))
        scrollable_body2 = Scrollable(frame2)
        self.button_frame_2 = ButtonMaker(scrollable_body2,
                                            column_title='2dVars',
                                            buttons=dimensions['2d'], 
                                            xrds=xrds,
                                            canvasobject=mapper,
                                            clicked_button=self.clicked_button,
                                            move_buttons=move_buttons,
                                            resample_buttons=resp_buttons)

        self.button_frame_2.pack()
        scrollable_body2.update()

        # 1d variables 
        lbl = tk.Label(self, text="1dVar", bg='yellow', borderwidth=3, relief="raised", fg="black")
        lbl.grid(column=1, row=4, sticky=(E, W))
        frame1 = tk.Frame(self)
        frame1.grid(column=1, row=5)
        scrollable_body1 = Scrollable(frame1)
        self.button_frame_1 = ButtonMaker(scrollable_body1,
                                            column_title='1dVars',
                                            buttons=dimensions['1d'], 
                                            xrds=xrds,
                                            clicked_button=self.clicked_button,
                                            canvasobject=mapper,
                                            move_buttons=move_buttons,
                                            resample_buttons=resp_buttons)
                                
        self.button_frame_1.pack()
        scrollable_body1.update()

       # now add the mapper...
        mapper(self)


        # label stuff below the plot
        # make the text for the box
        xrtext1 = "\n".join(["%s : %s"%(x, xrds.dims[x]) for x in xrds.dims.keys()])
        xrtext2 = "\n".join([l[4:] for l in str(xrds.coords).split("\n")[1:]])

        BottomFrame = tk.Frame(self, bg='green')
        BottomFrame.grid(column=0, row=6, columnspan=9, rowspan=1, sticky=(N, S, E, W))

        # add the dimesnions info 
        tk.Label(BottomFrame, text='Dimensions',bg='purple').grid(column=0, row=0, sticky=(N, S, E, W))
        labeldim      = tk.Label(BottomFrame, text=xrtext1, bg='gray')
        labeldim.grid(column=0, row=1,sticky=(N, S, E, W))


        # now add labels and the info itself 
        tk.Label(BottomFrame, text='Coordinates',bg='gray').grid(column=1, row=0, sticky=(N, S, E, W))
        labelcoord    = tk.Label(BottomFrame, text=xrtext2)
        labelcoord.grid(column=1, row=1, sticky=(N, S, E, W))

        # get some attributes of the variable that we are looking at... 
        tk.Label(BottomFrame, text='Variable Attributes', bg='purple').grid(column=2, row=0, sticky=(N, S, E, W))
        labelcoord    = tk.Label(BottomFrame, textvariable=self.clicked_button)
        labelcoord.grid(column=2, row=1, sticky=(N, S, E, W))
        

        # make another frame thing to the right of the main plotting area
        # make a drop down menu...  
        # RightFrame = tk.Frame(self, bg='red')
        # RightFrame.grid(column=9, row=2, columnspan=2, sticky=(N, S, E, W))

        # lbrsp=tk.Label(RightFrame, text="Resample").grid(column=0, row=0, sticky=(N, S, E, W))
        # variable = StringVar(RightFrame)
        # variable.set("one") # default value
        # w = OptionMenu(RightFrame, variable, "Month", "Week", "Day", "Hour")
        # w.grid(column=0, row=1, sticky=(N, S, E, W))

        mainloop()
