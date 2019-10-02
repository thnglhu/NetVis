from ipaddress import *

# a computer only connect to a switch
class Computer:
    def __init__(self, mac, ip_addr, ip_net):
        self.switch = None
        self.mac = mac
        self.ip_addr = ip_address(ip_addr)
        self.ip_net = ip_network(ip_net)

    # switch in this case is similar to default gateway
    def add_switch(self, switch):
        self.switch = switch

    def send(self, message, receiver):
        print("forward to switch " + self.switch.mac)
        self.switch.forward(message, self, receiver)

    def receive(self, message, sender):
        print("received from " + sender.mac + ": " + message)

# a switch only connects to a router
class Switch:
    def __init__(self, mac, *computers):
        self.router = None
        self.mac = mac
        self.table = []
        if computers is not None:
            for computer in computers:
                self.table.append(computer)
                computer.add_switch(self)

    def add_router(self, router):
        self.router = router
        self.table.append(router)

    def forward(self, message, sender, receiver):
        for item in self.table:
            if item.mac == receiver.mac:
                print("forward to computer " + item.mac)
                item.receive(message, sender)
                break


# Assumption router only connect to 1 switch
class Router:
    def add_rule(self, network, device):
        self.rules[ip_network(network)] = device

    def __init__(self, mac, ip_net, switch):
        self.mac = mac
        self.rules = {}
        self.add_rule(ip_network(ip_net), switch)
        switch.add_router(self)

    def add_router(self, router):
        pass

    def forward(self, message, sender, receiver):
        for ip_net, dev in self.rules:
            if receiver.ip_net == ip_net:
                print("forward to " + dev.mac)
                dev.forward(self, message, sender, receiver)


# net 1
pc1 = Computer("0000.0000.0001", "192.168.1.1", "192.168.1.0/24")
pc2 = Computer("0000.0000.0002", "192.168.1.2", "192.167.1.0/24")
switch1 = Switch("0000.0000.00S1", pc1, pc2)
router1 = Router("000C.0000.00R1", "192.168.1.0/24", switch1)
router1.add_rule("192.168.1.0/24", switch1)

# net 2
pc3 = Computer("0000.0000.0003", "10.10.0.1", "10.10.0.0/16")
switch2 = Switch("0000.0000.00S2", pc3)

# test
pc1.send("hallo pc2", pc2)      #working
pc1.send("hallo pc3", pc3)      #not working with router
