from .vertex import Vertex
from ..port import Port
from .hub import Hub
from threading import Thread
from time import sleep, time
import setting

from ..Frame.Data import BroadcastFrame
from ..Frame.Data import MulticastFrame
from ..Frame.Data.bpdu import BPDU

from Resource import get_image


class Switch(Hub):

    # region Canvas declaration
    def __init__(self, canvas, info):
        super().__init__(canvas, info)
        self.ports = {
            Port(port['name'], self, port.get('id')): {
                'state': 'designated',
                'mode': 'forwarding',
            } for port in info['ports']
        }
        for zipped in zip(self.ports, info['ports']):
            zipped[0].mac_address = zipped[1]['mac_address']
        self.mac_table = dict()
        self.type = 'switch'
        self['image'] = self['on-image'] if self.active else self['off-image']
        Thread(target=self.__checker).start()

    def _set_image(self):
        self['on-image'] = get_image('_switch-on')
        self['off-image'] = get_image('_hub-off')

    def save(self):
        result = super().save()
        return result
    # endregion

    # region Logical
    def __checker(self):
        wait_time = 5
        while not self.destroyed and self.active:
            if setting.time_scale.get() != 0:
                has = False
                for key, value in self.mac_table.copy().items():
                    if time() - value['time'] > wait_time * 100 / setting.time_scale.get():
                        self.mac_table.pop(key)
                        has = True
                if has:
                    self.update()
            sleep(0.1)

    def __stp_thread(self):
        wait_time = 2
        start_time = time()
        while not self.destroyed and self.active:
            if self.attributes.get('stp'):
                try:
                    if self['stp']['id'] == self['stp']['root_id'] and isinstance(self.ports, dict):
                        for port, info in self.ports.items():
                            frame = BPDU(
                                port.mac_address,
                                self['stp']['root_id'],
                                self['stp']['path_cost'],
                                self['stp']['id'],
                                port.mac_address,
                                0
                            )
                            port.send(frame)
                            info['state'] = 'designated'
                except KeyError:
                    return
            else:
                return
            while not self.destroyed and self.active:
                if setting.time_scale.get() == 0 or time() - start_time < wait_time * 100 / setting.time_scale.get():
                    sleep(0.01)
                else:
                    start_time = time()
                    break

        if not self.active and not self.destroyed:
            self.deactivate_stp()

    def receive(self, frame, port):
        if isinstance(frame, MulticastFrame):
            if self.attributes.get('stp') and frame.destination == "01:80:C2:00:00:00" and isinstance(frame, BPDU):
                self.stp_handling(port, frame)
                return True
            return False
        if self.ports[port]['state'] == 'blocked':
            return False
        if frame:
            self.mac_table[frame.source] = {
                'port': port,
                'time': time(),
            }
            self.update()
        if isinstance(frame, BroadcastFrame) or frame.destination not in self.mac_table:
            for other in self.ports:
                if other != port and self.ports[other]['state'] != 'blocked':
                    other.send(frame)
            return True
        elif frame.destination in self.mac_table and self.mac_table[frame.destination]['port'] != port:
            self.mac_table[frame.destination]['port'].send(frame)
        else:
            return False
        return True

    def disconnect(self, port):
        for key, value in self.mac_table.copy().items():
            if value['port'] == port:
                self.mac_table.pop(key)
        self.update()
        pass

    def activate_stp(self):
        self.ports = {
            key: {
                'state': 'designated',
                'mode': 'forwarding',
            } for key in self.ports
        }
        self['stp'] = {
            'priority': 32768,
            'id': id(self),
            'root_id': id(self),
            'path_cost': 0,
        }
        Thread(target=self.__stp_thread).start()

    def deactivate_stp(self):
        if self.attributes.get('stp'):
            self.attributes.pop('stp')

    def stp_handling(self, sender_port, bpdu):
        cost = bpdu.root_path_cost + 100 / sender_port.link.bandwidth
        if self['stp']['root_id'] > bpdu.root_switch:
            self['stp']['root_id'] = bpdu.root_switch
            self['stp']['path_cost'] = cost
            self.ports[sender_port]['state'] = 'root'
            for port in self.ports:
                if port != sender_port:
                    self.ports[port]['state'] = 'designated'
                    port.send(BPDU(
                        port.mac_address,
                        self['stp']['root_id'],
                        cost,
                        self['stp']['id'],
                        port.mac_address,
                        bpdu.age + 1
                    ))
            self.update()
        elif self['stp']['root_id'] == bpdu.root_switch:
            if self['stp']['path_cost'] == cost:
                for port in self.ports:
                    if port != sender_port:
                        port.send(BPDU(
                            port.mac_address,
                            self['stp']['root_id'],
                            cost,
                            self['stp']['id'],
                            port.mac_address,
                            bpdu.age + 1
                        ))
            elif self['stp']['path_cost'] > cost:
                self.ports[sender_port]['state'] = 'root'
                for port in self.ports:
                    if port != sender_port:
                        self.ports[sender_port]['state'] = 'designated'
                        port.send(BPDU(
                            port.mac_address,
                            self['stp']['root_id'],
                            cost,
                            self['stp']['id'],
                            port.mac_address,
                            bpdu.age + 1
                        ))
            else:
                if self['stp']['id'] > bpdu.sender_switch:
                    self.ports[sender_port]['state'] = 'blocked'
                    self.update()
    # endregion
