#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# GUI module generated by PAGE version 4.25.1
#  in conjunction with Tcl version 8.6
#    Sep 25, 2019 08:35:56 AM +07  platform: Windows NT

import sys


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
from tkinter import StringVar


def vp_start_gui():
    #Starting point when module is the main routine.
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
        label = tk.Label(
            self.tw,
            text=self.text,
            justify='left',
            background="#ffffff",
            relief='solid',
            borderwidth=1,
            wraplength=self.wraplength)
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
            command=gui_support.save_file_as,
            font="TkMenuFont",
            foreground="#000000",
            label="Save as...")

        self.sub_menu.add_separator()

        self.sub_menu.add_command(
            background="#ffffff",
            command=gui_support.print_file,
            font="TkMenuFont",
            foreground="#000000",
            label="Print")

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
            command=gui_support.undo,
            font="TkMenuFont",
            foreground="#000000",
            label="Undo")

        self.sub_menu_edit.add_command(
            background="#ffffff",
            command=gui_support.redo,
            font="TkMenuFont",
            foreground="#000000",
            label="Redo")

        self.sub_menu_edit.add_separator()

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

        self.nested_menu_edit.add_command(
            background="#ffffff",
            command=gui_support.find_node,
            font="TkMenuFont",
            foreground="#000000",
            label="Find Node")

        self.nested_menu_edit.add_command(
            background="#ffffff",
            command=gui_support.find_edge,
            font="TkMenuFont",
            foreground="#000000",
            label="Find Edge")

        self.nested_menu_edit.add_separator()

        self.sub_menu_edit.add_command(
            background="#ffffff",
            command=gui_support.cut,
            font="TkMenuFont",
            foreground="#000000",
            label="Cut")

        self.sub_menu_edit.add_command(
            background="#ffffff",
            command=gui_support.copy,
            font="TkMenuFont",
            foreground="#000000",
            label="Copy")

        self.sub_menu_edit.add_command(
            background="#ffffff",
            command=gui_support.paste,
            font="TkMenuFont",
            foreground="#000000",
            label="Paste")

        self.sub_menu_edit.add_command(
            background="#ffffff",
            command=gui_support.select_all,
            font="TkMenuFont",
            foreground="#000000",
            label="Select All")

        # ---------------------------Toolbar: Node-------------------------#
        self.menubar.add_cascade(
            menu=self.sub_menu_node,
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="Node")

        self.sub_menu_node.add_command(
            background="#ffffff",
            command=gui_support.select_all_nodes,
            font="TkMenuFont",
            foreground="#000000",
            label="Select All")

        self.sub_menu_node.add_command(
            background="#ffffff",
            command=gui_support.deselect_all_nodes,
            font="TkMenuFont",
            foreground="#000000",
            label="Deselect All")

        self.sub_menu_node.add_command(
            background="#ffffff",
            command=gui_support.add_node,
            font="TkMenuFont",
            foreground="#000000",
            label="Add Node")

        self.sub_menu_node.add_command(
            background="#ffffff",
            command=gui_support.remove_node,
            font="TkMenuFont",
            foreground="#000000",
            label="Remove Node")

        self.sub_menu_node.add_command(
            background="#ffffff",
            command=gui_support.rename_node,
            font="TkMenuFont",
            foreground="#000000",
            label="Rename Node")

        self.sub_menu_node.add_separator()

        self.sub_menu_node.add_command(
            background="#ffffff",
            command=gui_support.select_node_properties,
            font="TkMenuFont",
            foreground="#000000",
            label="Select Node Properties")

        self.sub_menu_node.add_separator()

        self.sub_menu_node.add_command(
            background="#ffffff",
            command=gui_support.change_all_nodes_color,
            font="TkMenuFont",
            foreground="#000000",
            label="Change All Nodes Color")

        self.sub_menu_node.add_command(
            background="#ffffff",
            command=gui_support.change_all_nodes_size,
            font="TkMenuFont",
            foreground="#000000",
            label="Change All Nodes Size")

        self.sub_menu_node.add_command(
            background="#ffffff",
            command=gui_support.change_all_nodes_shape,
            font="TkMenuFont",
            foreground="#000000",
            label="Change All Nodes Shape")

        self.sub_menu_node.add_separator()

        self.sub_menu_node.add_command(
            background="#ffffff",
            command=gui_support.change_all_nodes_label_size,
            font="TkMenuFont",
            foreground="#000000",
            label="Change All Node's Label Size")

        self.sub_menu_node.add_command(
            background="#ffffff",
            command=gui_support.change_all_nodes_label_color,
            font="TkMenuFont",
            foreground="#000000",
            label="Change All Node's Label Color")

        # ---------------------------Toolbar: Edge-------------------------#
        self.menubar.add_cascade(
            menu=self.sub_menu_edge,
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="Edge")

        self.sub_menu_edge.add_command(
            background="#ffffff",
            command=gui_support.select_all_edges,
            font="TkMenuFont",
            foreground="#000000",
            label="Select All")

        self.sub_menu_edge.add_command(
            background="#ffffff",
            command=gui_support.deselect_all_edges,
            font="TkMenuFont",
            foreground="#000000",
            label="Deselect All")

        self.sub_menu_edge.add_separator()

        self.sub_menu_edge.add_command(
            background="#ffffff",
            command=gui_support.add_edge,
            font="TkMenuFont",
            foreground="#000000",
            label="Add Edge")

        self.sub_menu_edge.add_command(
            background="#ffffff",
            command=gui_support.remove_edge,
            font="TkMenuFont",
            foreground="#000000",
            label="Remove Edge")

        self.sub_menu_edge.add_separator()

        self.sub_menu_edge.add_command(
            background="#ffffff",
            command=gui_support.select_edge_properties,
            font="TkMenuFont",
            foreground="#000000",
            label="Select Edge Properties")

        self.sub_menu_edge.add_separator()

        self.sub_menu_edge.add_command(
            background="#ffffff",
            command=gui_support.change_all_edges_label,
            font="TkMenuFont",
            foreground="#000000",
            label="Change Edge Label")

        self.sub_menu_edge.add_command(
            background="#ffffff",
            command=gui_support.change_all_edges_color,
            font="TkMenuFont",
            foreground="#000000",
            label="Change Edge Color")

        self.sub_menu_edge.add_command(
            background="#ffffff",
            command=gui_support.change_all_edges_weight,
            font="TkMenuFont",
            foreground="#000000",
            label="Change Edge Weight")

        # ---------------------------Toolbar: Network-------------------------#
        self.menubar.add_cascade(
            menu=self.sub_menu_network,
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="Network")

        # ---------------------------Toolbar: Filter-------------------------#
        self.menubar.add_cascade(
            menu=self.sub_menu_filter,
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="Filter")

        # ---------------------------Toolbar: Analyze-------------------------#
        self.menubar.add_cascade(
            menu=self.sub_menu_analyze,
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="Analyze")

        # ---------------------------Toolbar: Options-------------------------#
        self.menubar.add_cascade(
            menu=self.sub_menu_options,
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="Options")

        # ---------------------------Toolbar: Settings-------------------------#
        self.menubar.add_cascade(
            menu=self.sub_menu_settings,
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="Settings")

        # ---------------------------Toolbar: Help-------------------------#
        self.menubar.add_cascade(
            menu=self.sub_menu_help,
            background="#ffffff",
            font="TkMenuFont",
            foreground="#000000",
            label="Help")

        # ---------------------------Canvas-------------------------#

        self.main_canvas = tk.Canvas(top)
        self.main_canvas.place(
            relx=0.25,
            rely=0.115,
            relheight=0.85,
            relwidth=0.55)
        self.main_canvas.configure(
            borderwidth="0",
            background="#DCDCDC")

        self.main_canvas.create_rectangle(50, 25, 150, 75, fill="blue")

        # ---------------------------Control Panel-------------------------#
        self.control_panel = tk.Frame(top)
        self.control_panel.place(
            relx=0.005,
            rely=0.105,
            relheight=0.90,
            relwidth=0.24)
        self.control_panel.configure(
            background="#FaFaFa",
            takefocus="0")

        # ---------------------------Data Panel-------------------------#
        self.data_panel = tk.Frame(top)

        self.data_panel.place(
            relx=0.805,
            rely=0.105,
            relheight=0.90,
            relwidth=0.19)
        self.data_panel.configure(background="#ffffff")

        # ---------------------------Top Panel-------------------------#
        self.top_panel = tk.Frame(top)
        self.top_panel.place(
            relx=0.005,
            rely=0.005,
            relheight=0.1,
            relwidth=0.99)
        self.top_panel.configure(background="#ffffff")

        # ---------------------------Top Panel: Open-------------------------#
        self.add_file_image = ImageTk.PhotoImage(file="resource/icons/add_file.png")
        self.add_file_button = tk.Button(self.top_panel)
        self.add_file_button.place(
            anchor=tk.CENTER,
            relx=0.02,
            rely=0.5,
            height=55,
            width=55)
        self.add_file_button.configure(
            image=self.add_file_image,
            command=gui_support.open_file,
            borderwidth=0)

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
            image=self.new_file_image,
            command=gui_support.create_new_file)

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
            image=self.save_file_image,
            command=gui_support.save_file,
            borderwidth=0)

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
            image=self.search_image,
            borderwidth=0)
        self.search_box = tk.Text(self.top_panel)
        self.search_box.place(
            anchor=tk.CENTER,
            relx=0.255,
            rely=0.5,
            heigh=25,
            width=150)
        self.search_box.configure(bg="#DCDCDC")

        self.separator = ttk.Separator(self.top_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.32, rely=0.2, width=4, height=42)

        search_button_tooltip = CreateToolTip(self.search_button, "Enter the node's name to search for it")

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
            image=self.add_node_image,
            command=gui_support.add_node,
            borderwidth=0)

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
            image=self.remove_node_image,
            command=gui_support.remove_node,
            borderwidth=0)

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
            image=self.zoom_in_image,
            command=gui_support.zoom_in,
            borderwidth=0)

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
            image=self.zoom_out_image,
            command=gui_support.zoom_out,
            borderwidth=0)

        self.separator = ttk.Separator(self.top_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.53, rely=0.2, width=4, height=42)

        zoom_out_tooltip = CreateToolTip(self.zoom_out_button, "Zoom out")

        # ---------------------------Top Panel: Node Properties-------------------------#
        self.node_properties_image = ImageTk.PhotoImage(file="resource/icons/node_properties.png")
        self.node_properties_button = tk.Button(self.top_panel)
        self.node_properties_button.place(
            anchor=tk.CENTER,
            relx=0.56,
            rely=0.5,
            height=55,
            width=55)
        self.node_properties_button.configure(
            image=self.node_properties_image,
            command=gui_support.select_node_properties,
            borderwidth=0)

        node_properties_tooltip = CreateToolTip(self.node_properties_button, "Edit a node's properties such as device type, label, color, connectivity,... ")

        # ---------------------------Top Panel: Edge Properties-------------------------#
        self.edge_properties_image = ImageTk.PhotoImage(file="resource/icons/edge_properties.png")
        self.edge_properties_button = tk.Button(self.top_panel)
        self.edge_properties_button.place(
            anchor=tk.CENTER,
            relx=0.605,
            rely=0.5,
            height=55,
            width=55)
        self.edge_properties_button.configure(
            image=self.edge_properties_image,
            command=gui_support.select_edge_properties,
            borderwidth=0)

        self.separator = ttk.Separator(self.top_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.635, rely=0.2, width=4, height=42)

        edge_properties_tooltip = CreateToolTip(self.edge_properties_button, "Edit an edge's properties such as bandwidth, throughput, delay, label, connectivity,...")

        # ---------------------------Top Panel: Filter-------------------------#
        self.filter_image = ImageTk.PhotoImage(file="resource/icons/filter.png")
        self.filter_button = tk.Button(self.top_panel)
        self.filter_button.place(
            anchor=tk.CENTER,
            relx=0.665,
            rely=0.5,
            height=55,
            width=55)
        self.filter_button.configure(
            image=self.filter_image,
            borderwidth=0)

        self.separator = ttk.Separator(self.top_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.695, rely=0.2, width=4, height=42)

        filter_tooltip = CreateToolTip(self.filter_button, "Filter nodes, edges with specific features")

        # ---------------------------Top Panel: Settings-------------------------#
        self.settings_image = ImageTk.PhotoImage(file="resource/icons/settings.png")
        self.settings_button = tk.Button(self.top_panel)
        self.settings_button.place(
            anchor=tk.CENTER,
            relx=0.9,
            rely=0.5,
            height=55,
            width=55)
        self.settings_button.configure(
            image=self.settings_image,
            command=settings_popup_window,
            borderwidth=0)

        self.separator = ttk.Separator(self.top_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.94, rely=0.2, width=4, height=42)

        settings_tooltip = CreateToolTip(self.settings_button, "Settings")

        # ---------------------------Top Panel: Help-------------------------#
        self.help_image = ImageTk.PhotoImage(file="resource/icons/help.png")
        self.help_button = tk.Button(self.top_panel)
        self.help_button.place(
            anchor=tk.CENTER,
            relx=0.98,
            rely=0.5,
            height=55,
            width=55)
        self.help_button.configure(
            image=self.help_image,
            borderwidth=0)

        help_tooltip = CreateToolTip(self.help_button, "Help")

        # ---------------------------Control Panel: Title-------------------------#
        self.control_panel_title = tk.Label(self.control_panel, text="Control Panel", font=("Helvetica", 12, "bold"))
        self.control_panel_title.place(
            anchor=tk.CENTER,
            relx=0.16,
            rely=0.05)

        self.control_panel_title.configure(bg="#fafafa")

        self.separator = ttk.Separator(self.control_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.05, rely=0.07, width=280, height=4)

        # ---------------------------Control Panel: Node-------------------------#
        self.node_title = tk.Label(self.control_panel, text="Node", font=("Helvetica", 12, "bold"))
        self.node_title.place(
            anchor=tk.CENTER,
            relx=0.12,
            rely=0.095)

        self.node_title.configure(bg="#fafafa")

        self.separator = ttk.Separator(self.control_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.05, rely=0.11, width=280, height=4)

        '''
        # ---------------------------Control Panel: Node: Add a node-------------------------#
        self.add_node_title = tk.Label(self.control_panel, text="Add Devices:", font=("Helvetica", 12))
        self.add_node_title.place(
            anchor='w',
            relx=0.05,
            rely=0.14)

        self.add_node_title.configure(bg="#fafafa")

        self.node_type = StringVar()
        self.add_node_combobox = ttk.Combobox(self.control_panel, state='readonly', textvariable=self.node_type, width=10)
        self.add_node_combobox['values'] = ("Computer", "Hub", "Modem", "Router", "Switch")
        self.add_node_combobox.current(0)
        self.add_node_combobox.place(
            anchor='w',
            relx=0.4,
            rely=0.14)

        self.node_button = tk.Button(self.control_panel, text="Apply", command=gui_support.add_node)
        self.node_button.place(anchor='w', relx=0.8, rely=0.14)
        self.node_button.configure(bg="#fafafa")

        '''
        # ---------------------------Control Panel: Node: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.14)

        self.sample_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Node: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.18)

        self.sample_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Node: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.22)

        self.sample_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Node: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.26)

        self.sample_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Node: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.3)

        self.sample_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Node: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.34)

        self.sample_title.configure(bg="#fafafa")

        self.separator = ttk.Separator(self.control_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.05, rely=0.37, width=280, height=4)

        # ---------------------------Control Panel: Edge-------------------------#
        self.edge_title = tk.Label(self.control_panel, text="Edge", font=("Helvetica", 12, "bold"))
        self.edge_title.place(
            anchor=tk.CENTER,
            relx=0.12,
            rely=0.395)

        self.edge_title.configure(bg="#fafafa")

        self.separator = ttk.Separator(self.control_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.05, rely=0.41, width=280, height=4)

        # ---------------------------Control Panel: Edge: Add an edge-------------------------#
        self.add_edge_title = tk.Label(self.control_panel, text="Add Edge:", font=("Helvetica", 12))
        self.add_edge_title.place(
            anchor='w',
            relx=0.05,
            rely=0.44)

        self.add_edge_title.configure(bg="#fafafa")

        self.edge_type = StringVar()
        self.add_edge_combobox = ttk.Combobox(self.control_panel, state='readonly', textvariable=self.edge_type)
        self.add_edge_combobox['values'] = ("Wired", "Wireless")
        self.add_edge_combobox.current(0)
        self.add_edge_combobox.place(
            anchor='w',
            relx=0.4,
            rely=0.44)

        # ---------------------------Control Panel: Edge: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.48)

        self.sample_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Edge: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.52)

        self.sample_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Edge: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.56)

        self.sample_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Edge: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.6)

        self.sample_title.configure(bg="#fafafa")

        self.separator = ttk.Separator(self.control_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.05, rely=0.63, width=280, height=4)

        # ---------------------------Control Panel: Analyze-------------------------#
        self.analyze_title = tk.Label(self.control_panel, text="Analyze", font=("Helvetica", 12, "bold"))
        self.analyze_title.place(
            anchor='w',
            relx=0.05,
            rely=0.655)

        self.analyze_title.configure(bg="#fafafa")

        self.separator = ttk.Separator(self.control_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.05, rely=0.675, width=280, height=4)

        # ---------------------------Control Panel: Analyze: Show Bottleneck-------------------------#
        self.bottleneck_title = tk.Label(self.control_panel, text="Show Bottleneck:", font=("Helvetica", 12))
        self.bottleneck_title.place(
            anchor='w',
            relx=0.05,
            rely=0.71)

        self.bottleneck_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Analyze: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.75)

        self.sample_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Analyze: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.79)

        self.sample_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Analyze: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.83)

        self.sample_title.configure(bg="#fafafa")

        # ---------------------------Control Panel: Analyze: Sample-------------------------#
        self.sample_title = tk.Label(self.control_panel, text="Sample", font=("Helvetica", 12))
        self.sample_title.place(
            anchor='w',
            relx=0.05,
            rely=0.87)

        self.sample_title.configure(bg="#F0F0F0")

        # ---------------------------Data Panel: Title-------------------------#
        self.data_panel_title = tk.Label(self.data_panel, text="Data Panel", font=("Helvetica", 12, "bold"))
        self.data_panel_title.place(
            anchor=tk.CENTER,
            relx=0.15,
            rely=0.05)

        self.separator = ttk.Separator(self.data_panel, orient=tk.VERTICAL)
        self.separator.place(relx=0.05, rely=0.07, width=280, height=4)

        self.data_panel_title.configure(bg="#F0F0F0")

        top.configure(menu=self.menubar)

if __name__ == '__main__':
    vp_start_gui()
