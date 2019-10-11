from PIL import ImageTk, Image
from threading import Thread
from time import sleep

root_paths = "resource/images/"
image_paths = dict()
ig = image_paths
ig['hub'] = "hub.png"
ig['pc-on'] = "pc-on.gif"
ig['pc-on-focus'] = "pc-on-focus.gif"
ig['pc-off'] = "pc-off.gif"
ig['router'] = "router.gif"
ig['switch'] = "switch.gif"
ig['arp'] = "arp.png"
ig['arp-reply'] = "arp-reply.png"
ig['mail'] = "mail.png"
ig['opened-mail'] = "opened-mail.png"
ig['stp'] = "stp.png"
ig['icmp'] = "icmp.png"
ig['icmp-reply'] = "icmp-reply.png"
ig['icmp-unreachable'] = "icmp-unreachable.png"
ig['hello-reply'] = "hello-reply.png"
ig['hello'] = "hello.png"
ig['rip'] = "rip.png"
ig['open-file'] = "open-file.png"
ig['save-file'] = "save-file.png"
ig['new-file'] = "new-file.png"
ig['about'] = "about.gif"
# image_paths['abc'] = "D:/Users/thngl/Documents/GitHub/NetVis/resource/images/pc-on.gif"

image_cache = dict()


def get_image(name):
    item = image_cache.get(name)
    if not item:
        if image_paths.get(name) is None:
            image_paths[name] = name + ".png"
        item = image_cache[name] = StaticImage.factory(image_paths[name])
    return item


class StaticImage:
    data = object

    def __init__(self, file_name):
        self.setup(file_name)

    def setup(self, file_name):
        self.data = ImageTk.PhotoImage(file=file_name)

    def get_image(self):
        return self.data

    def subscribe(self, target, function, canvas):
        pass

    def unsubscribe(self, target):
        pass

    @staticmethod
    def factory(file_name, **kwargs):
        file_name = root_paths + file_name
        extension = file_name.split('.')[-1]
        if extension == 'gif':
            return AnimatedImage(file_name)
        else:
            return StaticImage(file_name)


class AnimatedImage(StaticImage):
    index = 0
    thread = object
    time = 1

    def setup(self, file_name):
        print('dasd')
        self.subscribers = dict()
        self.data = list()
        source = Image.open(file_name)
        try:
            from itertools import count
            for index in count(1):
                self.data.append(ImageTk.PhotoImage(source.copy()))
                source.seek(index)
        except EOFError:
            pass
        self.time = source.info['duration'] / 1000
        thread = Thread(target=self.__change_image)
        thread.start()

    def __change_image(self):
        try:
            while True:
                if len(self.subscribers) > 0:
                    self.index = (self.index + 1) % len(self.data)
                    for subscriber, pack in self.subscribers.items():
                        pack[0](pack[1])
                sleep(self.time)
        except RuntimeError:
            pass

    def get_image(self):
        return self.data[self.index]

    def subscribe(self, target, function, canvas):
        self.subscribers[target] = (function, canvas)

    def unsubscribe(self, target):
        print(len(self.subscribers))
        if target in self.subscribers:
            self.subscribers.pop(target)
        print(len(self.subscribers))
