import customtkinter
import tkinter as tk
from tkinter import ttk
from metaread import get_varnames, xreader, get_dimensions

import matplotlib.pyplot as plt 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure


window_width = 1000
window_height = 700



def set_mousewheel(widget, command):
    """Activate / deactivate mousewheel scrolling when 
    cursor is over / not over the widget respectively."""
    widget.bind("<Enter>", lambda _: widget.bind_all('<MouseWheel>', command))
    widget.bind("<Leave>", lambda _: widget.unbind_all('<MouseWheel>'))



class Scrollable(tk.Frame):
    """
       Make a frame scrollable with scrollbar on the right.
       After adding or removing widgets to the scrollable frame,
       call the update() method to refresh the scrollable area.
    """

    def __init__(self, frame):

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=True)

        self.canvas = customtkinter.CTkCanvas(frame, width=window_width*.2, height=80, yscrollcommand=scrollbar.set)
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
                 **kwargs):

        super().__init__(*args, **kwargs)
        self.xrds = xrds 
        self.canvasobject = canvasobject

        lbl=tk.Label(self, text=column_title, bg='red')
#        lbl.grid(row=0, column=0, pady=1, fill=tk.BOTH)
        lbl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for i, button in enumerate(buttons):
            _cmd = lambda x=button: self.button_event(x)

            self.button_x = ttk.Button(self, text=str(button), command=_cmd)
#            self.button_x.grid(row=i+1, column=0, padx=1, pady=1, fill=tk.BOTH)
            self.button_x.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def button_event(self, x):
        # clear the existing canvas...
        if self.xrds is not None:
            self.xrds.get(x).plot(ax=self.canvasobject.ax)
            self.canvasobject.canvas.draw()
        else:
            print("no data loaded to plot")


class MplMaker(tk.Frame):

    def __init__(self, frame):
#        super().__init__(*args, **kwargs)

        self.fig = Figure(dpi=100)
        self.ax = self.fig.add_subplot(111)
#        ax.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
        self.canvas = FigureCanvasTkAgg(self.fig, frame)

    def __call__(self, frame):
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)



class App(customtkinter.CTk):
    def __init__(self, thefile):
        super().__init__()
        ipadding = {'ipadx': .1, 'ipady': .1}

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



        # 4d variables 
        if len(dimensions['4d']) > 0:
            frame4 = tk.Frame(self)
            frame4.pack(**ipadding, expand=False, fill=tk.Y, side=tk.LEFT)
            scrollable_body4 = Scrollable(frame4)
            self.button_frame_4 = ButtonMaker(scrollable_body4,
                                              column_title='4dVars',
                                              buttons=dimensions['4d'], 
                                              xrds=xrds,
                                              canvasobject=mapper)
            self.button_frame_4.pack()
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
                                              canvasobject=mapper)
            self.button_frame_3.pack()
            scrollable_body2.update()


        # 2d variables 
        if len(dimensions['2d']) > 0:
            frame2 = tk.Frame(self)
            frame2.pack(**ipadding, expand=False, fill=tk.Y, side=tk.LEFT)
            scrollable_body2 = Scrollable(frame2)
            self.button_frame_2 = ButtonMaker(scrollable_body2,
                                              column_title='2dVars',
                                              buttons=dimensions['2d'], 
                                              xrds=xrds,
                                              canvasobject=mapper)                                              
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
                                              canvasobject=mapper)                                              
            self.button_frame_1.pack()
            scrollable_body1.update()

        mapper(self)
       
        # DIMENSIONS
        # frame01 = ttk.Frame(self)#  width=.2*window_width, height=.9*window_height)
        # frame01.pack(**ipadding, expand=True, fill=tk.BOTH, side=tk.LEFT)
        # scrollable_body01 = Scrollable(frame01)


        ### ADD MPL PLOT 


        # xrdescription = tk.Label(self, text=str(xrds))
        # xrdescription.pack(**ipadding, expand=True, fill=tk.BOTH, side=tk.LEFT)





        # make a yellow box next to the 2nd rown of buttons 
