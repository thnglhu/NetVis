import tkinter
from Visual.Canvas import Canvas
from Visual.Extension import VerticalScrollable
from controller import Controller
from functools import partial
from Resource import get_image
import setting


class Application:

    def __init__(self, master):
        self.root = master
        self.root.title('NETT')

        self.canvas_frame = tkinter.Frame(master)
        self.canvas_frame.place(y=60, relx=0, width=-450, relwidth=1.0, height=-60, relheight=1)
        self.canvas = Canvas(self.canvas_frame, background='lightgray')
        self.canvas.config(highlightthickness=1, highlightbackground='darkgray')
        self.canvas.pack(fill=tkinter.BOTH, padx=5, pady=5, expand=1)

        self.warped_info_frame = tkinter.Frame(self.root)
        self.warped_info_frame.place(y=100, x=-450, relx=1, width=450, height=-220, relheight=1)
        self.info_frame = tkinter.Frame(self.warped_info_frame)
        self.info_frame.config(highlightthickness=1, highlightbackground='lightgray')
        self.info_frame.pack(fill=tkinter.BOTH, padx=5, pady=5, expand=1)
        self.scrollable_frame = VerticalScrollable(self.info_frame)

        self.filter_frame = tkinter.Frame(self.root)
        self.filter_frame.place(y=-100, x=-445, relx=1, rely=1, width=440, height=95)
        self.filter_frame.config(highlightthickness=1, highlightbackground='lightgray')

        self.top_frame = tkinter.Frame(self.root)
        self.top_frame.place(x=5, y=5, width=-10, relwidth=1, height=55)
        self.top_frame.config(highlightthickness=2, highlightbackground='lightgray')

        tkinter.Label(self.root, text="Information: ", font=(None, 12)).place(x=-450, relx=1, y=70)
        tkinter.Label(self.root, text="Filter: ", font=(None, 10)).place(x=-450, relx=1, y=-125, rely=1)

        self.modification_button = tkinter.Button(self.root, text='Modify')
        self.modification_button.place(x=-50, relx=1, y=70, anchor="ne")
        self.apply_button = tkinter.Button(self.root, text='Apply')
        self.apply_button.place(x=-5, relx=1, y=70, anchor="ne")

        tkinter.Label(master, text='Time scale:').place(x=-200, y=25, relx=1)
        setting.time_scale = tkinter.IntVar(master)
        self.time_bar = tkinter.Scale(self.top_frame, from_=0, to=100, variable=setting.time_scale, orient=tkinter.HORIZONTAL)
        setting.time_scale.set(20)
        self.time_bar.place(x=-105, y=0, relx=1)
        controller = Controller(self)

        self.menu_bar = tkinter.Menu(master)

        self.file_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=controller.new)
        self.file_menu.add_command(label="Open", command=controller.load)
        self.file_menu.add_command(label="Save", command=controller.save)
        self.file_menu.add_separator()
        self.sample_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.sample_menu.add_command(label="Simple", command=partial(controller.load, 'Sample/example-0.json'))
        self.sample_menu.add_command(label="Switch", command=partial(controller.load, 'Sample/example-1.json'))
        self.sample_menu.add_command(label="Broadcast Storm", command=partial(controller.load, 'Sample/example-2.json'))
        self.sample_menu.add_command(label="Router", command=partial(controller.load, 'Sample/example-3.json'))
        self.sample_menu.add_command(label="Router Problems", command=partial(controller.load, 'Sample/example-4.json'))
        self.file_menu.add_cascade(label="Sample", menu=self.sample_menu)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=controller.exit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.new_file = tkinter.Button(self.top_frame, image=get_image('new-file').get_image(), borderwidth=0, command=controller.new)
        self.new_file.place(x=25, rely=0.5, anchor=tkinter.CENTER)

        self.load_file = tkinter.Button(self.top_frame, image=get_image('open-file').get_image(), borderwidth=0, command=controller.load)
        self.load_file.place(x=75, rely=0.5, anchor=tkinter.CENTER)

        self.save_file = tkinter.Button(self.top_frame, image=get_image('save-file').get_image(), borderwidth=0, command=controller.save)
        self.save_file.place(x=125, rely=0.5, anchor=tkinter.CENTER)

        self.zoom_out = tkinter.Button(self.top_frame, image=get_image('zoom-out').get_image(), borderwidth=0, command=controller.zoom_out)
        self.zoom_out.place(x=200, rely=0.5, anchor=tkinter.CENTER)

        self.zoom_in = tkinter.Button(self.top_frame, image=get_image('zoom-in').get_image(), borderwidth=0, command=controller.zoom_in)
        self.zoom_in.place(x=250, rely=0.5, anchor=tkinter.CENTER)

        self.add_device = tkinter.Button(self.top_frame, image=get_image('add-device').get_image(), borderwidth=0, command=partial(controller.add_device, "host"))
        self.add_device.place(x=325, rely=0.5, anchor=tkinter.CENTER)

        self.remove_device = tkinter.Button(self.top_frame, image=get_image('remove-device').get_image(), borderwidth=0, command=controller.remove_device)
        self.remove_device.place(x=375, rely=0.5, anchor=tkinter.CENTER)

        self.edit_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.edit_add_device = tkinter.Menu(self.edit_menu, tearoff=0)
        self.edit_add_device.add_command(label="Host", command=partial(controller.add_device, "host"))
        self.edit_add_device.add_command(label="Hub", command=partial(controller.add_device, "hub"))
        self.edit_add_device.add_command(label="Switch", command=partial(controller.add_device, "switch"))
        self.edit_add_device.add_command(label="Router", command=partial(controller.add_device, "router"))
        self.edit_menu.add_cascade(label="Add device", menu=self.edit_add_device)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.help_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Help Index", state='disabled')
        self.help_menu.add_command(label="About...", command=controller.about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.root.config(menu=self.menu_bar)
        self.root.protocol('WM_DELETE_WINDOW', controller.exit)


if __name__ == '__main__':
    root = tkinter.Tk()
    root.geometry("1280x1024")
    Application(root)
    root.mainloop()
