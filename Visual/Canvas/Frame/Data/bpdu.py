from .multicast_frame import MulticastFrame
from Resource import get_image


class BPDU(MulticastFrame):
    def __init__(self,
                 source,
                 root_switch,
                 root_path_cost,
                 sender_switch,
                 sender_port,
                 age,
                 max_age=10,
                 flag='TCA'):
        super().__init__(source, "01:80:C2:00:00:00", None)
        self.flag = flag
        self.root_switch = root_switch
        self.root_path_cost = root_path_cost
        self.sender_switch = sender_switch
        self.sender_port = sender_port
        self.age = age
        self.max_age = max_age

    def get_image(self):
        return get_image('stp')

    def get_name(self):
        return "stp"