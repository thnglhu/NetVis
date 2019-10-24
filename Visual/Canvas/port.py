class Port:

    # region Declaration
    def __init__(self, name, device, port_id=None, mac_address=None):
        self.name = name
        self.device = device
        self.link = None
        self.id = port_id if port_id else id(self)
        self.mac_address = mac_address
        self.active = True

    def save(self):
        result = {
            'id': self.id,
            'name': self.name,
        }
        if self.mac_address:
            result['mac_address'] = self.mac_address
        return result

    def destroy(self, collector):
        if self.link:
            self.link.destroy(collector)
    # endregion

    # region Logical
    def connect(self, link):
        self.link = link
        self.device.subscribe(link)

    def disconnect(self):
        self.device.disconnect(self)

    def send(self, frame):
        if self.active and self.link and self.link.active:
            self.link.send(frame, self)

    def enable(self):
        self.active = True
        if self.link:
            self.link.enable()

    def disable(self):
        self.active = False
        if self.link:
            self.link.disable()

    def receive(self, frame):
        return self.device.receive(frame, self)
    # endregion
