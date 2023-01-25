import customtkinter
import tkinter as tk
from tkinter import ttk
from metaread import get_varnames, xreader, get_dimensions
import numpy as np 

import matplotlib.pyplot as plt 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure


window_width = 1800
window_height = 2200

# # for plots...
# def reset_axsize(w,h, ax=None):
#     """ w, h: width, height in inches """
#     if not ax: ax=plt.gca()
#     l = ax.figure.subplotpars.left
#     r = ax.figure.subplotpars.right
#     t = ax.figure.subplotpars.top
#     b = ax.figure.subplotpars.bottom
#     figw = float(w)/(r-l)
#     figh = float(h)/(t-b)
#     ax.figure.set_size_inches(figw, figh)


# def set_mousewheel(widget, command):
#     """Activate / deactivate mousewheel scrolling when 
#     cursor is over / not over the widget respectively."""
#     widget.bind("<Enter>", lambda _: widget.bind_all('<MouseWheel>', command))
#     widget.bind("<Leave>", lambda _: widget.unbind_all('<MouseWheel>'))



class Scrollable(tk.Frame):
    """
       Make a frame scrollable with scrollbar on the right.
       After adding or removing widgets to the scrollable frame,
       call the update() method to refresh the scrollable area.
    """

    def __init__(self, frame):

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=True)

        self.canvas = customtkinter.CTkCanvas(frame, width=window_width*.1, height=80, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.canvas.yview)
        self.canvas.bind('<Configure>', self.__fill_canvas)

        # # base class initialization
        tk.Frame.__init__(self, frame)

        # # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0, 0, window=self, anchor=tk.NW)
        self.canvas.bind_all('<MouseWheel>', lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

    def __fill_canvas(self, event):
        "Enlarge the windows item to the canvas width"

        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width = canvas_width)

    def update(self):
        "Update the canvas and the scrollregion"

        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))
        # print("update")


class ButtonMaker(tk.Frame):
    def __init__(self, 
                 *args, 
                 xrds=None,
                 column_title=None,
                 buttons=None,
                 header_name=None, 
                 canvasobject=None,
                 clickers=None,
                 move_buttons=None,
                 **kwargs):

        super().__init__(*args, **kwargs)
        self.xrds = xrds 
        self.canvasobject = canvasobject
        self.original_size = canvasobject.fig.get_size_inches()
        self.clickers = clickers 
        self.move_buttons = move_buttons

        # now label stuff...
        lbl=tk.Label(self, text=column_title, bg='red')
#        lbl.grid(row=0, column=0, pady=1, fill=tk.BOTH)
        lbl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for i, button in enumerate(buttons):
            _cmd = lambda x=button: self.button_event(x)

            self.button_x = ttk.Button(self, text=str(button), command=_cmd)
#            self.button_x.grid(row=i+1, column=0, padx=1, pady=1, fill=tk.BOTH)
            self.button_x.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        

    def button_event(self, x):
        # get the value of the previous and next buttons
        # clear the existing canvas...
        #if len(self.canvasobject.fig.axes) > 1:
        #    self.canvasobject.fig.axes[1].remove()
            #reset_axsize(self.original_size[1], self.original_size[0], self.canvasobject.ax)

        # get the variable 
        plotting_variable = self.xrds.get(x) #.isel()#time=self.move_buttons.thetime.get())


        # MOVE THIS SOMEWHERE ELSE SO THAT IT DOESNT HAPPEN EVERY CLICK
        one_len_list = {}
        for i,k in enumerate(plotting_variable.shape):
            if k == 1:
                one_len_list[plotting_variable.dims[i]] = 0

        # just go ahead and select these -- makes dim size smaller 
        plotting_variable = plotting_variable.sel(**one_len_list)

# now check if there is a time like dimension
# time_coord = []
# possible_time_types = [np.dtype("<M8[ns]")] 
# for c in plotting_variable.coords:
# f c.dtype in possible_time_types
        
        
        # select the concat dim if it's in there. ..
        if "CONCAT_DIM" in list(plotting_variable.dims):
            plotting_variable = plotting_variable.isel(CONCAT_DIM=self.move_buttons.thetime.get())

        # get some info about the plotting variable ...        
        if len(plotting_variable.shape) > 5:
            pass

        if len(plotting_variable.shape) == 4:
            pass 

        if len(plotting_variable.shape) == 3: 
            plotting_variable.plot(ax=self.canvasobject.ax, 
                                   add_colorbar=False)
            self.canvasobject.canvas.draw()

        if len(plotting_variable.shape) == 2: 
            plotting_variable.plot(ax=self.canvasobject.ax, 
                                   add_colorbar=False)
            self.canvasobject.canvas.draw()

        if len(plotting_variable.shape) == 1: 
            plotting_variable.plot(ax=self.canvasobject.ax)
            self.canvasobject.canvas.draw()


        # print the click value 
        # print()


class cbmaker(tk.Frame):
    def __init__(self, 
                *args, 
                **kwargs):
        super().__init__(*args, **kwargs)

        self.spamVar = tk.StringVar()
        self.spamCB  = tk.Checkbutton(self, text='A', variable=self.spamVar, onvalue='yes', offvalue='no')

class MoveButtoner(tk.Frame):
    def __init__(self, frame):
        super().__init__()#K*args, **kwargs)
        self.thetime = tk.IntVar()
        self.thetime.set(0)

        _cmd_nxt = lambda x=1 : self.move_timestep(x)
        _cmd_prv = lambda x=-1 : self.move_timestep(x)

        self.next = ttk.Button(frame, text='Next', command=_cmd_nxt)
        self.prev = ttk.Button(frame, text='Prev', command=_cmd_prv)
        self.next.pack(fill=tk.BOTH, expand=True, side='left')
        self.prev.pack(fill=tk.BOTH, expand=True, side='left')
        
    def move_timestep(self,x):    
       newtime = x + self.thetime.get()
       self.thetime.set(newtime)
       print(self.thetime.get())

class MplMaker(tk.Frame):

    def __init__(self, frame):
        # super().__init__(*args, **kwargs)
        self.fig = Figure(dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, frame)

    def __call__(self, frame):
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, 
                                         fill=tk.BOTH, 
                                         expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, frame)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)



class App(customtkinter.CTk):

    def __init__(self, thefile):
        super().__init__()
        ipadding = {'ipadx': 1, 'ipady': .1}

        # make the screen show up so it is centered on the screen 
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        # set the position of the window to the center of the screen
#        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.thefile=thefile
       

        # read in the xarray stuff and make the buttons 
        datavars, coords = get_varnames(thefile)
        xrds = xreader(thefile) 
        dimensions = get_dimensions(xrds)
        mapper = MplMaker(self)

        # Label across the entire top of the frame 
        if type(thefile) == list:
            headerlabel = ".".join(thefile[0].split(".")[0:-1])+"*"
        else:
            headerlabel = thefile
        label1 = tk.Label(self, text=headerlabel, bg="green", fg="white")
        label1.pack(**{'ipadx': 5, 'ipady': 5}, fill=tk.X)

    
        # check buttons 
        frame02 = tk.Frame(self,  bg='purple', width=100, height=100)
        frame02.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)              
        checkbuttons1 = ttk.Checkbutton(frame02, text='foo')
        # checkbuttons1 = cbmaker(frame02)
        checkbuttons1.pack(side=tk.BOTTOM)

        frame00 = tk.Frame(self,  bg='orange', width=100, height=100)
        frame00.pack(fill=tk.BOTH, expand=True, side=tk.TOP)              
        move_buttons = MoveButtoner(frame00)

        
        # 4d variables 
        if len(dimensions['4d']) > 0:
            frame4 = tk.Frame(self)
            frame4.pack(**ipadding, expand=False, fill=tk.Y, side=tk.LEFT)
            scrollable_body4 = Scrollable(frame4)
            self.button_frame_4 = ButtonMaker(scrollable_body4,
                                              column_title='4dVars',
                                              buttons=dimensions['4d'], 
                                              xrds=xrds,
                                              canvasobject=mapper,
                                              clickers=checkbuttons1,
                                              move_buttons=move_buttons)

            self.button_frame_4.pack(fill=tk.Y)
            scrollable_body4.update()


        # 3d variables 
        if len(dimensions['3d']) > 0:
            frame3 = tk.Frame(self)
            frame3.pack(**ipadding, expand=False, fill=tk.Y, side=tk.LEFT)
            scrollable_body3 = Scrollable(frame3)
            self.button_frame_3 = ButtonMaker(scrollable_body3,
                                              column_title='3dVars',
                                              buttons=dimensions['3d'], 
                                              xrds=xrds,
                                              canvasobject=mapper,
                                              clickers=checkbuttons1,
                                              move_buttons=move_buttons)
            self.button_frame_3.pack()
            scrollable_body3.update()


        # 2d variables 
        if len(dimensions['2d']) > 0:
            frame2 = tk.Frame(self)
            frame2.pack(**ipadding, expand=False, fill=tk.Y, side=tk.LEFT)
            scrollable_body2 = Scrollable(frame2)
            self.button_frame_2 = ButtonMaker(scrollable_body2,
                                              column_title='2dVars',
                                              buttons=dimensions['2d'], 
                                              xrds=xrds,
                                              canvasobject=mapper,
                                              clickers=checkbuttons1,
                                              move_buttons=move_buttons)                                      
            self.button_frame_2.pack()
            scrollable_body2.update()


        if len(dimensions['1d']) > 0:
            frame1 = tk.Frame(self)
            frame1.pack(**ipadding, expand=False, fill=tk.Y, side=tk.LEFT)
            scrollable_body1 = Scrollable(frame1)
            self.button_frame_1 = ButtonMaker(scrollable_body1,
                                              column_title='1dVars',
                                              buttons=dimensions['1d'], 
                                              xrds=xrds,
                                              canvasobject=mapper,
                                              move_buttons=move_buttons)                                       
            self.button_frame_1.pack()
            scrollable_body1.update()

        # DIMENSIONS
        # frame01 = tk.Frame(self)#  width=.2*window_width, height=.9*window_height)
        # frame01.pack(**ipadding,  expand=False, fill=tk.Y, side=tk.LEFT)
        # scrollable_body01    = Scrollable(frame01)
        # self.button_frame_01 = ButtonMaker(scrollable_body01,
        #                                    column_title='Dimensions',
        #                                    buttons=['button', 'button', 'button'], 
        #                                    xrds=xrds,
        #                                    canvasobject=mapper,
        #                                    move_buttons=move_buttons)

#        self.button_frame_01.pack()
#        scrollable_body01.update()
        mapper(self)
       
        ### ADD MPL PLOT 


        # xrdescription = tk.Label(self, text=str(xrds))
        # xrdescription.pack(**ipadding, expand=True, fill=tk.BOTH, side=tk.LEFT)





        # make a yellow box next to the 2nd rown of buttons 
