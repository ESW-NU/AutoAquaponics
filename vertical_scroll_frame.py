'''
Code below found from GitHub in {ScrolledFrame.py}
{https://gist.github.com/JackTheEngineer/81df334f3dcff09fd19e4169dd560c59}
Used to create vertical scroll bar on Dashboard, modified for sizing and binding to mouse scroll
'''
import tkinter as tk
import functools
fp = functools.partial

class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self.canvas.config(width=interior.winfo_reqwidth())
        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())
        #this part binds scroll bar to mouse scroll
        def _on_mousewheel(event, scroll=0):
            if scroll == -1 or scroll == 1:
                self.canvas.yview_scroll(int(scroll), "units")
            else:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<Button-4>", fp(_on_mousewheel, scroll=-1))
            self.canvas.bind_all("<Button-5>", fp(_on_mousewheel, scroll=1))
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
            self.canvas.unbind_all("<MouseWheel>")

        tk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = tk.Canvas(self, bd=5, highlightthickness=0,bg="white",
                        yscrollcommand=vscrollbar.set)
        #self.canvas.config(width=100, height=580)
        self.canvas.config(width=50, height=520)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.canvasheight = 520

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(self.canvas)
        interior_id = self.canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)
  
        interior.bind('<Configure>', _configure_interior)
        self.canvas.bind('<Configure>', _configure_canvas)
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)