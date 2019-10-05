from network import data as dt

handler = dict()


def interface_arp_handler(interface, frame, **kwargs):
    arp = frame.packet
    if arp and isinstance(arp, dt.ARP) and arp.ip_target == interface.ip_address:
        if arp.is_reply:
            arp.func()
        else:
            reply = dt.Frame(interface.mac_address, frame.mac_source, arp.reply())
            interface.send(reply, kwargs.get('canvas'))
        return True
    return False


def hub_broadcast_handler(hub, frame, **kwargs):
    source = kwargs.get('source')
    for other in hub.others:
        if other is not source:
            hub.send(frame, other, kwargs.get('canvas'))


def router_forward_handler(router, frame, **kwargs):
    packet = frame.packet
    if packet and kwargs.get('receiver').mac_address == frame.mac_target:
        for network in router.routing_table:
            interface = router.routing_table[network]
            if packet.ip_target in network \
                    and packet.ip_target != interface.ip_address \
                    and kwargs.get('source') != interface:
                router.forward(interface, frame, kwargs.get('canvas'))
