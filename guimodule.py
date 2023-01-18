from tkinter import *
import matplotlib.pyplot as plt 



def build_gui(buttons,xrda):

    # The main tkinter window
    window = Tk()
    
    # setting the title and 
    window.title('Plotting in Tkinter')
    
    # setting the dimensions of 
    # the main window
    window.geometry("500x500")
    

    # go through each button 
    def cmd(x):
        # clear the existing canvas...
        plt.clf()
        xrda.get(x).plot()
        plt.show()

    for button in buttons:
#        button that would displays the plot

        _cmd = lambda x=button: cmd(x)
        plot_button = Button(master = window,
                             height = 2,
                             width = 20,
                             command = _cmd,
                             text = button)
                          
        # place the button
        # into the window
        plot_button.pack()


    return window 


