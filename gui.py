#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# GUI module generated by PAGE version 4.25.1
#  in conjunction with Tcl version 8.6
#    Sep 25, 2019 08:35:56 AM +07  platform: Windows NT

import sys

import resource

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk

    py3 = False
except ImportError:
    import tkinter.ttk as ttk

    py3 = True

import gui_support
from PIL import ImageTk, Image
from time import strftime, localtime, time
from functools import partial

def vp_start_gui():

    # Starting point when module is the main routine.

    global val, w, root
    root = tk.Tk()
    top = top_level(root)
    gui_support.init(root, top)
    root.mainloop()


w = None


def create_top_level(root, *args, **kwargs):
    # Starting point when module is imported by another program.
    global w, w_win, rt
    rt = root
    w = tk.Toplevel(root)
    top = top_level(w)
    gui_support.init(w, top, *args, **kwargs)
    return (w, top)


def destroy_top_level():
    global w
    w.destroy()
    w = None


def settings_popup_window():
    settings_popup = tk.Tk()

    settings_popup.geometry("300x500")
    settings_popup.title("Settings")

    button = ttk.Button(settings_popup, text="Okay")
    button.grid(row=1, column=0)

    settings_popup.mainloop()


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()


class top_level:
    def __init__(self, top=None):
        # This class configures and populates the toplevel window. top is the toplevel containing window.
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        top.title("PocketNet")
        top.configure(background="#ffffff")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")
        # FULLSCREEN
        root.attributes('-fullscreen', True)
        root.geometry("1024x1024")

        self.menubar = tk.Menu(top, font="TkMenuFont", bg=_bgcolor, fg=_fgcolor)

        self.sub_menu = tk.Menu(top, tearoff=0)
        self.sub_menu_edit = tk.Menu(top, tearoff=0)
        self.sub_menu_node = tk.Menu(top, tearoff=0)
        self.sub_menu_edge = tk.Menu(top, tearoff=0)
        self.sub_menu_network = tk.Menu(top, tearoff=0)
        self.sub_menu_filter = tk.Menu(top, tearoff=0)
        self.sub_menu_analyze = tk.Menu(top, tearoff=0)
        self.sub_menu_options = tk.Menu(top, tearoff=0)
        self.sub_menu_settings = tk.Menu(top, tearoff=0)
        self.sub_menu_help = tk.Menu(top, tearoff=0)

        # default_font = font.nametofont("TkDefaultFont")
        # default_font.configure(family="Rockwell", size=13)

        # ---------------------------Toolbar: File-------------------------#
        self.menubar.add_cascade(
            menu=self.sub_menu,
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="File")

        self.sub_menu.add_command(
            background="#ffffff",
            command=gui_support.create_new_file,
            font="TkMenuFont",
            foreground="#000000",
            label="New")

        self.sub_menu.add_command(
            background="#ffffff",
            command=gui_support.open_file,
            font="TkMenuFont",
            foreground="#000000",
            label="Open")

        self.sub_menu.add_separator()

        self.nested_menu_file = tk.Menu(self.sub_menu)
        self.sub_menu.add_cascade(menu=self.nested_menu_file,
                                  background="#ffffff",
                                  font="TkMenuFont",
                                  foreground="#000000",
                                  label="Recent Files")
        for file in ('File1.txt', 'File2.txt', 'File3.txt'):
            self.nested_menu_file.add_command(
                label=file,
                command=lambda: gui_support.open_recent_file)

        self.sub_menu.add_separator()

        self.sub_menu.add_command(
            background="#ffffff",
            command=gui_support.save_file,
            font="TkMenuFont",
            foreground="#000000",
            label="Save")

        self.sub_menu.add_command(
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="Save as...")

        self.sub_menu.add_separator()

        self.sub_menu.add_command(
            background="#ffffff",
            command=gui_support.close,
            font="TkMenuFont",
            foreground="#000000",
            label="Close")

        self.sub_menu.add_command(
            background="#ffffff",
            command=gui_support.exit_window,
            font="TkMenuFont",
            foreground="#000000",
            label="Exit")

        # ---------------------------Toolbar: Edit-------------------------#
        self.menubar.add_cascade(
            menu=self.sub_menu_edit,
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="Edit")

        self.sub_menu_edit.add_command(
            background="#ffffff",
            command=gui_support.zoom_in,
            font="TkMenuFont",
            foreground="#000000",
            label="Zoom In")

        self.sub_menu_edit.add_command(
            background="#ffffff",
            command=gui_support.zoom_out,
            font="TkMenuFont",
            foreground="#000000",
            label="Zoom Out")

        self.sub_menu_edit.add_separator()

        self.nested_menu_edit = tk.Menu(self.sub_menu_edit)
        self.sub_menu_edit.add_cascade(
            menu=self.nested_menu_edit,
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="Find")

        # ---------------------------Canvas-------------------------#

        self.main_canvas = tk.Canvas(top)
        self.main_canvas.place(
            #relx=0.25,
            relx=0.01,
            # rely=0.065,
            rely = 0.1,
            relheight=0.89,
            relwidth=0.50)
        self.main_canvas.configure(
            borderwidth="0",
            background="#DCDCDC")

        # ---------------------------Control Panel-------------------------#
        """self.control_panel = tk.Frame(top)
        self.control_panel.place(
            relx=0.005,
            rely=0.105,
            relheight=0.90,
            relwidth=0.24)
        self.control_panel.configure(
            background="#FAFAFA",
            takefocus="0")"""

        # ---------------------------Data Panel-------------------------#
        self.data_panel = tk.Frame(top)

        self.data_panel.place(
            relx=0.51,
            rely=0.105 - 0.05,
            relheight=0.85,
            relwidth=0.49)
        self.data_panel.configure(background="#ffffff")

        # ---------------------------Top Panel-------------------------#
        self.top_panel = tk.Frame(top)
        self.top_panel.place(
            relx=0.005,
            rely=0.005,
            relheight=0.075,
            relwidth=0.99)
        self.top_panel.configure(background="#FFFFFF")

        # ---------------------------Top Panel: Open-------------------------#
        # self.add_file_image = ImageTk.PhotoImage(file="resource/icons/add_file.png")
        self.add_file_button = tk.Button(self.top_panel)
        self.add_file_button.place(
            anchor=tk.CENTER,
            relx=0.02,
            rely=0.5,
            height=55,
            width=55)
        self.add_file_button.configure(
            image=resource.get_image('open-file').get_image(),
            command=gui_support.open_file,
            borderwidth=0,
            bg="#ffffff")

        add_file_tooltip = CreateToolTip(self.add_file_button, "Open a graph. The file extension should be GraphML, GDF or GEXF")

        # ---------------------------Top Panel: New-------------------------#
        self.new_file_image = ImageTk.PhotoImage(file="resource/icons/new_file.png")
        self.new_file_button = tk.Button(self.top_panel)
        self.new_file_button.place(
            anchor=tk.CENTER,
            relx=0.065,
            rely=0.5,
            height=55,
            width=55)
        self.new_file_button.configure(
            borderwidth=0,
            image=resource.get_image('new-file').get_image(),
            command=gui_support.create_new_file,
            bg="#ffffff")

        new_file_tooltip = CreateToolTip(self.new_file_button,"Create an empty GraphML file")

        # ---------------------------Top Panel: Save-------------------------#
        self.save_file_image = ImageTk.PhotoImage(file="resource/icons/save_file.png")
        self.save_file_button = tk.Button(self.top_panel)
        self.save_file_button.place(
            anchor=tk.CENTER,
            relx=0.11,
            rely=0.5,
            height=55,
            width=55)
        self.save_file_button.configure(
            image=resource.get_image('save-file').get_image(),
            command=gui_support.save_file,
            borderwidth=0,
            bg="#ffffff")

        self.separator = ttk.Separator(self.top_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.14, rely=0.2, width=4, height=42)

        save_file_tooltip = CreateToolTip(self.save_file_button, "Save the file")

        # ---------------------------Top Panel: Search-------------------------#
        self.search_image = ImageTk.PhotoImage(file="resource/icons/search.png")
        self.search_button = tk.Button(self.top_panel)
        self.search_button.place(
            anchor=tk.CENTER,
            relx=0.172,
            rely=0.5,
            height=55,
            width=55)
        self.search_button.configure(
            image=resource.get_image('find').get_image(),
            borderwidth=0,
            command=gui_support.find_device,
            bg="#ffffff")
        self.search_box = tk.Entry(self.top_panel)
        self.search_box.place(
            anchor=tk.CENTER,
            relx=0.255,
            rely=0.5,
            heigh=25,
            width=150)
        self.search_box.bind('<Return>', gui_support.find_device)

        self.separator = ttk.Separator(self.top_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.32,rely=0.2,width=4, height=42)

        search_tooltip = CreateToolTip(self.search_button, "Enter the node's name to search for it")

        # ---------------------------Top Panel: Add Node-------------------------#
        self.add_node_image = ImageTk.PhotoImage(file="resource/icons/add_node.png")
        self.add_node_button = tk.Button(self.top_panel)
        self.add_node_button.place(
            anchor=tk.CENTER,
            relx=0.35,
            rely=0.5,
            height=55,
            width=55)
        self.add_node_button.configure(
            image=resource.get_image('add-device').get_image(),
            command=gui_support.add_node,
            borderwidth=0,
            bg="#ffffff")

        add_node_tooltip = CreateToolTip(self.add_node_button, "Add node")

        # ---------------------------Top Panel: Remove Node-------------------------#
        self.remove_node_image = ImageTk.PhotoImage(file="resource/icons/remove_node.png")
        self.remove_node_button = tk.Button(self.top_panel)
        self.remove_node_button.place(
            anchor=tk.CENTER,
            relx=0.395,
            rely=0.5,
            height=55,
            width=55)
        self.remove_node_button.configure(
            image=resource.get_image('remove-device').get_image(),
            command=gui_support.remove_node,
            borderwidth=0,
            bg="#ffffff")

        remove_node_tooltip = CreateToolTip(self.remove_node_button, "Remove node")

        self.separator = ttk.Separator(self.top_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.425, rely=0.2, width=4, height=42)

        # ---------------------------Top Panel: Zoom In-------------------------#
        self.zoom_in_image = ImageTk.PhotoImage(file="resource/icons/zoom_in.png")
        self.zoom_in_button = tk.Button(self.top_panel)
        self.zoom_in_button.place(
            anchor=tk.CENTER,
            relx=0.455,
            rely=0.5,
            height=55,
            width=55)
        self.zoom_in_button.configure(
            image=resource.get_image('zoom-in').get_image(),
            command=gui_support.zoom_in,
            borderwidth=0,
            bg="#ffffff")

        zoom_in_tooltip = CreateToolTip(self.zoom_in_button, "Zoom in")

        # ---------------------------Top Panel: Zoom Out-------------------------#
        self.zoom_out_image = ImageTk.PhotoImage(file="resource/icons/zoom_out.png")
        self.zoom_out_button = tk.Button(self.top_panel)
        self.zoom_out_button.place(
            anchor=tk.CENTER,
            relx=0.5,
            rely=0.5,
            height=55,
            width=55)
        self.zoom_out_button.configure(
            image=resource.get_image('zoom-out').get_image(),
            command=gui_support.zoom_out,
            borderwidth=0,
            bg="#ffffff")

        self.separator = ttk.Separator(self.top_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.53, rely=0.2, width=4, height=42)

        zoom_out_tooltip = CreateToolTip(self.zoom_out_button, "Zoom out")

        # ---------------------------Top Panel: About-------------------------#
        def about_popup_window():
            about_popup = tk.Toplevel()

            # about_popup.geometry("619x660")
            about_popup.title("About")

            # canvas = tk.Canvas(about_popup)
            # canvas.pack(fill=tk.BOTH, expand=0)
            image = resource.get_image('about')
            label = tk.Label(about_popup, image=image.get_image())
            label.pack()
            # gif = canvas.create_image(0, 0, image=image.get_image())

            def update_gif(_):
                label.configure(image=image.get_image())
                # canvas.itemconfigure(gif, image=image.get_image())

            image.subscribe(label, update_gif, None)

        self.about_image = ImageTk.PhotoImage(file="resource/icons/about.png")
        self.about_button = tk.Button(self.top_panel)
        self.about_button.place(
            anchor=tk.CENTER,
            relx=0.98,
            rely=0.5,
            height=55,
            width=55)
        self.about_button.configure(
            image=self.about_image,
            command=about_popup_window,
            borderwidth=0,
            bg="#ffffff")

        self.timer = tk.Label(self.top_panel)
        self.timer.place(
            relx=0.8,
            rely=0.5
        )

        def change_time():
            self.timer.configure(text=strftime('%H:%M:%S', localtime(time())))
            self.top_panel.after(500, change_time)

        change_time()

        help_tooltip = CreateToolTip(self.about_button, "About")

        # ---------------------------Data Panel: Title-------------------------#
        self.data_panel_title = tk.Label(self.data_panel, text="Information", font=("Helvetica", 12, "bold"))
        self.data_panel_title.place(
            anchor=tk.CENTER,
            relx=0.15,
            rely=0.05)
        self.data_panel_title.configure(bg="#ffffff")

        self.separator = ttk.Separator(self.data_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.05, rely=0.07, width=590, height=3)

        # ---------------------------Data Panel: Node Data Panel-------------------------#
        self.node_data_panel = tk.Frame(self.data_panel)
        self.node_data_panel.place(
            relx=0.06,
            rely=0.1,
            relheight=0.8,
            relwidth=0.9)
        self.node_data_panel.configure(background="#fafafa")

        self.filter_panel = tk.Frame(self.data_panel)
        self.filter_panel.place(
            relx=0.05,
            rely=0.1 + 0.8,
            relheight=0.15,
            relwidth=0.9
        )
        """
        # ---------------------------Data Panel: Edge Title-------------------------#
        self.separator = ttk.Separator(self.data_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.05, rely=0.43, width=280, height=4)

        self.edge_data_title = tk.Label(self.data_panel, text="Edge Data", font=("Rockwell", 12, "bold"))
        self.edge_data_title.place(
            anchor=tk.CENTER,
            relx=0.2,
            rely=0.455)
        self.edge_data_title.configure(bg="#F0F0F0")

        self.separator = ttk.Separator(self.data_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.05, rely=0.465, width=280, height=4)

        # ---------------------------Data Panel: Edge Data Panel-------------------------#
        self.edge_data_panel = tk.Frame(self.data_panel)
        self.edge_data_panel.place(
            relx=0,
            rely=0.47,
            relheight=0.5,
            relwidth=1)
        self.edge_data_panel.configure(background="#fafbf0")

        # ---------------------------Log Text-------------------------------------------#
        self.log_text = tk.Text(self.edge_data_panel, wrap="word", state="disabled")
        self.log_text.place(
            relx=0.02,
            rely=0.02,
            width=350,
            height=800
        )
        self.log_scrollbar = tk.Scrollbar(command=self.log_text.yview())
        self.log_text['yscrollcommand'] = self.log_scrollbar.set

        # ---------------------------Coordinates-------------------------#
        self.coordinate_x_label = tk.Label(top, font=("Rockwell", 9))
        self.coordinate_x_label.place(relx=0.0, rely=0.99, anchor='w')
        self.coordinate_x_label.configure(bg="#F0F0F0")

        self.coordinate_y_label = tk.Label(top, font=("Rockwell", 9))
        self.coordinate_y_label.place(relx=0.015, rely=0.99, anchor='w')
        self.coordinate_y_label.configure(bg="#F0F0F0")
        """
        top.configure(menu=self.menubar)


if __name__ == '__main__':
    vp_start_gui()
