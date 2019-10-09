import tkinter as tk
import tkinter.ttk as ttk


class Form:
    data = dict()
    head = None


    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    @staticmethod
    def grid(item, **kwargs):
        item.grid(
            row=kwargs.get('row'),
            column=kwargs.get('column'),
            padx=kwargs.get('padx'),
            pady=kwargs.get('pady'),
            rowspan=kwargs.get('rowspan'),
            columnspan=kwargs.get('columnspan'),
            sticky=kwargs.get('sticky', tk.W),
        )

    def label(self, root=None, **kwargs):
        if root is None:
            root = self.head
        label = tk.Label(root, text=kwargs.get('text'), font=("Helvetica",12))
        Form.grid(label, **kwargs)
        return label

    def entry(self, root=None, **kwargs):
        if root is None:
            root = self.head
        entry = tk.Entry(root)
        Form.grid(entry, **kwargs)
        return entry

    def tree_view(self, root=None, **kwargs):
        if root is None:
            root = self.head
        header = kwargs.get('headers')
        tree = ttk.Treeview(
            root,
            columns=[str(i + 1) for i in range(len(header) - 1)]
        )

        tree.configure()
        Form.grid(tree, **kwargs)
        tree.heading('#0', text=header[0])
        tree.column('#0', width=70)
        for i in range(len(header) - 1):
            tree.heading(str(i + 1), text=header[i + 1])
            tree.column(str(i + 1), width=70)
        return tree

    def button(self, root=None, **kwargs):
        if root is None:
            root = self.head
        button = ttk.Button(root, text=kwargs.get('text'), command=kwargs.get('command'))
        self.grid(button, **kwargs)
        return button

    def get_info(self):
        print(self.data)
        return {
            key: Form.extract(value) for key, value in self.data.items()
        }

    @staticmethod
    def extract(item):
        if isinstance(item, tk.Entry):
            return item.get()
        elif isinstance(item, ttk.Treeview):
            result = list()
            for child in item.get_children():
                result.append([item.item(child)['text']] + item.item(child)['values'])
            return result
        elif isinstance(item, dict):
            return {
                key: Form.extract(value) for key, value in item.items()
            }

    @staticmethod
    def entry_set(entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    @staticmethod
    def tree_append(tree, *values):
        tree.insert('', 0, text=values[0], values=values[1:])