class Gif:
    def __init__(self, *args, **kwargs):
        self.images = args
        self.start = 0
        self.time = kwargs.get('delay', 1)

