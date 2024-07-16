'''
CREATES A CURSOR TO SHOW LOCATION ON A GRAPH

In main program, write:
cursorobj = addCursor.CursorClass(ax, x, y) #create a CursorClass object
where x and y are vectors defining the graph
'''
import matplotlib.pyplot as plt
import numpy as np

#class to view cursor
class CursorClass(object):
    def __init__(self, ax, x, y):
        self.ax = ax
        self.ly = ax.axvline(color='yellow', alpha=0.5)
        self.marker, = ax.plot([0], [0], marker="o", color="red", zorder=3)
        self.x = x
        self.y = y
        self.txt = ax.text(0.7, 0.9, '')


    #specify location upon hovering mouse over graph
    def mouse_event(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            indx = np.searchsorted(self.x, [x])[0]
            x = self.x[indx]
            y = self.y[indx]
            self.ly.set_xdata(x)
            self.marker.set_data([x], [y])
            self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
            self.txt.set_position((x, y))
            self.ax.figure.canvas.draw_idle()
        else:
            return
