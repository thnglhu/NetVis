from Visual.Canvas.graph import Graph
import tkinter.filedialog as fd
from Visual.Extension.info_form import InfoForm
from Visual.Extension.context_menu import ContextMenu
from Visual.Extension.addition_form import AdditionForm
from Resource import get_image
from setting import visible
from functools import partial
import tkinter


class Controller:
    def __init__(self, application):
        self.application = application
        self.graph = Graph(application.canvas)
        self.info_form = InfoForm(application.scrollable_frame, self.graph, application.modification_button, application.apply_button)
        self.context_menu = ContextMenu(application.root, application.canvas, self.graph)
        self.addition_form = AdditionForm(application.root, self.graph)
        application.canvas.subscribe(self.info_form.load, 'Button-1', 'object')
        application.canvas.subscribe(self.info_form.delete, 'Button-1', 'object')
        application.canvas.subscribe(self.context_menu.load, 'Button-3', 'object')
        application.canvas.subscribe(self.context_menu.second_load, 'Button-1', 'object')
        application.canvas.subscribe(self.addition_form.load, 'Button-1', 'location')
        self.setup_filter(application.filter_frame)
        self.about_image = None

    def new(self):
        self.graph.destroy()

    def load(self, filename=None):
        if not filename:
            filename = fd.askopenfilename(title="Select file", filetypes=(("json files", "*.json"), ))
        if filename:
            self.graph.destroy()
            self.graph.load(filename)

    def save(self):
        filename = fd.asksaveasfilename(title="Save as ...", defaultextension='json', filetypes=(("json files", "*.json"), ))
        if filename:
            self.graph.save(filename)

    def exit(self):
        import sys
        import Resource
        self.graph.destroy()
        self.application.root.destroy()
        self.application.root.quit()
        Resource.clean()
        sys.exit()

    def setup_filter(self, frame):
        count = 0

        def switch(_label, _name, _):
            visible[_name] ^= True
            _status = visible[_name]
            _image = get_image(_name if _status else _name + '-off')
            _label.configure(image=_image.get_image())

        for name, status in visible.items():
            image = get_image(name if status else name + '-off')
            label = tkinter.Label(frame, image=image.get_image())
            label.grid(row=count // 5, column=count % 5)
            label.bind('<Button-1>', partial(switch, label, name))
            count += 1

    def add_device(self, device_type):
        self.addition_form.add_device(device_type)

    def remove_device(self):
        self.info_form.remove = True

    def zoom_in(self):
        self.application.canvas.zoom((self.application.canvas.winfo_width() / 2, self.application.canvas.winfo_height() / 2), potential=1.2)

    def zoom_out(self):
        self.application.canvas.zoom((self.application.canvas.winfo_width() / 2, self.application.canvas.winfo_height() / 2), potential=1/1.2)

    def about(self):
        import Resource
        from PIL import ImageTk, Image
        def about_popup_window():

            about_popup = tkinter.Toplevel()
            about_popup.title("About")

            if not self.about_image:
                self.about_image = Resource.get_image('_about')

            image = self.about_image
            label = tkinter.Label(about_popup, image=image.get_image())
            label.pack()

            def update_gif():
                if tkinter.Toplevel.winfo_exists(about_popup):
                    label.configure(image=image.get_image())
                else:
                    self.about_image.unsubscribe(self.about_image)

            self.about_image.subscribe(self.about_image, update_gif)

        about_popup_window()
