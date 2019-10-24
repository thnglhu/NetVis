from .Device import classification
from .Link import Link


class Graph:
    def __init__(self, canvas):
        self.devices = set()
        self.links = set()
        self.canvas = canvas

    def load(self, file_name):
        with open(file_name) as json_file:
            import json
            data = json.load(json_file)
            ports = dict()
            for device_data in data['devices']:
                device = self.add_device(device_data)
                for port in device.get_ports():
                    ports[port.id] = port
            for link in data['links']:
                self.add_link(ports[link['ids'][0]], ports[link['ids'][1]], link['bandwidth'])
        self.fix_display()

    def fix_display(self):
        min_pos = (0, 0)
        max_pos = (0, 0)
        for device in self.devices:
            position = device.position
            min_pos = min(min_pos[0], position[0]), min(min_pos[1], position[1])
            max_pos = max(max_pos[0], position[0]), max(max_pos[1], position[1])
        self.canvas.scale_to_fit(min_pos, max_pos, 100)

    def save(self, path):
        from json import dump, dumps
        with open(path, "w") as json:
            info = {
                'devices': [
                    device.save() for device in self.devices
                ],
                'links': [
                    link.save() for link in self.links
                ],
            }
            dump(info, json)

    def add_device(self, info):
        device_type = classification.get(info['type'])
        if device_type:
            device = device_type(self.canvas, info)
            if device:
                self.devices.add(device)
                device.display()
                return device
        return None

    def add_link(self, port_a, port_b, bandwidth):
        if port_a and port_b:
            self.remove_link(port_a.link)
            self.remove_link(port_b.link)
            link = Link(port_a, port_b, bandwidth, self.canvas)
            if link:
                self.links.add(link)
                link.display()
                return link
        return None

    def remove_as_collector(self, collector):
        for device in collector.get('device', {}):
            self.devices.remove(device)
        for link in collector.get('link', {}):
            self.links.remove(link)

    def remove_device(self, device):
        collector = {
            'device': set(),
            'link': set()
        }
        device.destroy(collector)
        self.remove_as_collector(collector)

    def remove_link(self, link):
        if link:
            collector = {
                'link': set()
            }
            link.destroy(collector)
            self.remove_as_collector(collector)

    def destroy(self):
        collector = {
            'device': set(),
            'link': set()
        }
        for device in self.devices:
            device.destroy(collector)
        self.remove_as_collector(collector)


