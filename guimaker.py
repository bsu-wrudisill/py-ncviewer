import customtkinter
import tkinter as tk
from tkinter import ttk
from metaread import get_varnames, xreader

import matplotlib.pyplot as plt 
# import matplotlib
# matplotlib.use("TkAgg")Z
# from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# from matplotlib.figure import Figure


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

        self.canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.canvas.yview)
        self.canvas.bind('<Configure>', self.__fill_canvas)

        # base class initialization
        tk.Frame.__init__(self, frame)

        # assign this obj (the inner frame) to the windows item of the canvas
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
        print("update")


class ButtonMaker(tk.Frame):
    def __init__(self, 
                 *args, 
                 xrds=None,
                 buttons=None,
                 header_name=None, 
                 **kwargs):

        super().__init__(*args, **kwargs)
        self.xrds = xrds 
       
        for i, button in enumerate(buttons):
            _cmd = lambda x=button: self.button_event(x)

            self.button_x = ttk.Button(self, text=str(button), command=_cmd)
            # self.button_x.grid(row=i+1, column=0, padx=1, pady=1)
            self.button_x.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def button_event(self, x):
        # clear the existing canvas...
        if self.xrds is not None:
            plt.clf()
            self.xrds.get(x).plot()
            plt.show()
        else:
            print("no data loaded to plot")


class MplMaker(tk.Frame):

    def __init__(self, frame):
#        super().__init__(*args, **kwargs)

        fig = Figure(figsize=(5,5), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)



class App(customtkinter.CTk):
    def __init__(self, thefile):
        super().__init__()
        ipadding = {'ipadx': .1, 'ipady': .1}

        window_width = 1000
        window_height = 700

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

        # Build the columns ...
        # cwid = .2
        # chgt = .9   
        # toppadfrac = .05
        # yleftpad = 40 



        # these are the variables
        # label1 = tk.Label(self, text=thefile, bg="green", fg="white")
        # label1.pack(**{'ipadx': 5, 'ipady': 5}, fill=tk.X)


        # 4d variables 
        frame1 = ttk.Frame(self)#
#        frame1.place(relwidth=cwid, relheight=chgt, y=toppadfrac*window_height)
        frame1.pack(**ipadding, expand=False, fill=tk.Y, side=tk.LEFT)
        scrollable_body1 = Scrollable(frame1)


        # these are the dimensions
        frame2 = ttk.Frame(self)#  width=.2*window_width, height=.9*window_height)
#        frame2.place(relwidth=cwid, relheight=chgt, x=window_width*cwid, y=toppadfrac*window_height)
        frame2.pack(**ipadding, expand=True, fill=tk.BOTH, side=tk.LEFT)
        scrollable_body2 = Scrollable(frame2)


        # this is the text box for some stuff 
#        frame3 = tk.Label(self, text='Box 2', bg="green", fg="white")
#        frame3.place(x=window_width*cwid*2, 
#                     relheight=.1, 
#                     relwidth= (window_width - window_width*cwid*2 - yleftpad)/window_width,
#                     y=window_height - toppad - .1*window_height)
        
#        frame4 = tk.Label(self, text='Box 3', bg="red", fg="white")
#        frame4.



        ### ADD MPL PLOT 
#        MplMaker(frame4)
        xrdescription = tk.Label(self, text=str(xrds))
 #        xrdescription.place(x=window_width*cwid*2, 
 #                   relheight= .77, 
 #                   relwidth= (window_width - window_width*cwid*2 - yleftpad)/window_width,
 #                   y=toppadfrac*window_height)
        xrdescription.pack(**ipadding, expand=True, fill=tk.BOTH, side=tk.LEFT)





        #### CREATE THE BUTTONS ###
        # create One set of buttons
        self.button_frame_1 = ButtonMaker(scrollable_body1,
                                          buttons=datavars, 
                                          xrds=xrds)
                                          

        self.button_frame_1.pack()
        scrollable_body1.update()


        #create buttons for the dimensions
        self.button_frame_2 = ButtonMaker(scrollable_body2,
                                          buttons=coords, 
                                          xrds=xrds)
        self.button_frame_2.pack()
        scrollable_body2.update()



        # make a yellow box next to the 2nd rown of buttons 
