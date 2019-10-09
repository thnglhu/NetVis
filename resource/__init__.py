from PIL import ImageTk, Image
from threading import Thread
from time import sleep
image_paths = dict()
ig = image_paths
ig['hub'] = "resource/images/hub.png"
ig['pc-on'] = "resource/images/pc-on.gif"
ig['pc-on-focus'] = "resource/images/pc-on-focus.gif"
ig['pc-off'] = "resource/images/pc-off.gif"
ig['router'] = "resource/images/router.png"
ig['switch'] = "resource/images/switch.gif"
ig['arp'] = "resource/images/arp.png"
ig['arp-reply'] = "resource/images/arp-reply.png"
ig['mail'] = "resource/images/mail.png"
ig['opened-mail'] = "resource/images/opened-mail.png"
ig['stp'] = "resource/images/stp.png"
ig['icmp'] = "resource/images/icmp.png"
ig['icmp-reply'] = "resource/images/icmp-reply.png"
ig['icmp-unreachable'] = "resource/images/icmp-unreachable.png"
ig['rip'] = "resource/images/rip.png"
# image_paths['abc'] = "D:/Users/thngl/Documents/GitHub/NetVis/resource/images/pc-on.gif"

image_cache = dict()


def get_image(name):
    item = image_cache.get(name)
    if not item:
        # item = image_cache[name] = ImageTk.PhotoImage(file=image_paths[name]))
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
        extension = file_name.split('.')[-1]
        if extension == 'gif':
            return AnimatedImage(file_name)
        else:
            return StaticImage(file_name)


class AnimatedImage(StaticImage):
    index = 0
    subscribers = dict()
    thread = object
    time = 1

    def setup(self, file_name):
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
        if target in self.subscribers:
            self.subscribers.pop(target)
