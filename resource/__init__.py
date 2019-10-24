import time, itertools, threading
from PIL import ImageTk, Image
root_paths = "Resource/Images/"
cache = dict()
paths = dict()


def clean():
    for image in cache.values():
        image.clear()


def get_image(name):
    global cache, paths
    item = cache.get(name)
    if item:
        return item
    else:
        pre_name = name
        if name[0] == '_':
            name = name[1:] + ".gif"
        else:
            name = name + ".png"
        cache[pre_name] = _Image.factory(name)
        return cache[pre_name]


class _Image:

    def __init__(self, path):
        self.active = True
        self.path = path
        self.image = object
        self.setup(path)

    def setup(self, path):
        self.image = ImageTk.PhotoImage(file=path)

    def get_image(self):
        return self.image

    def subscribe(self, key, delegate):
        pass

    def unsubscribe(self, key):
        pass

    def clear(self):
        pass

    @staticmethod
    def factory(name):
        path = root_paths + name
        extension = path.split('.')[-1]
        if extension == 'gif':
            return _AnimatedImage(path)
        else:
            return _Image(path)


class _AnimatedImage(_Image):

    def __init__(self, path):
        self.active = True
        self.path = path
        self.subscribers = dict()
        self.delay = list()
        self.index = 0
        self.thread = None
        super().__init__(path)

    def setup(self, path):
        self.image = list()
        origin = Image.open(path)
        try:
            for index in itertools.count(1):
                copy = origin.copy()
                self.image.append(ImageTk.PhotoImage(copy))
                self.delay.append(copy.info['duration'] / 1000)
                origin.seek(index)
        except EOFError:
            pass
        self.thread = threading.Thread(target=self.__animate)
        self.thread.start()

    def __animate(self):
        while True:
            if not self.active:
                return
            for delegate in self.subscribers.copy().values():
                delegate()
            time.sleep(self.delay[self.index])
            self.index += 1
            self.index %= len(self.image)

    def get_image(self):
        return self.image[self.index]

    def subscribe(self, key, delegate):
        self.subscribers[key] = delegate

    def unsubscribe(self, key):
        self.subscribers.pop(key)

    def clear(self):
        if self.thread.is_alive():
            self.active = False
            self.thread.join()

