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


def interface_icmp_handler(interface, frame, **kwargs):
    icmp = frame.packet
    if icmp and isinstance(icmp, dt.ICMP):
        if icmp.ip_target == interface.ip_address:
            if icmp.unreachable:
                print("Unreachable")
            else:
                if icmp.state == "echo":
                    icmp.route.append(interface)
                    icmp.state = "reply"
                    reply = dt.Frame(interface.mac_address, frame.mac_source, icmp.reply())
                    interface.send(reply, kwargs.get('canvas'))
                elif icmp.state == "reply":
                    print(icmp.route)
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
        check = True
        for network in router.routing_table:
            rule = router.routing_table[network]
            interface = rule['interface']
            if packet.ip_target in network \
                    and packet.ip_target != interface.ip_address \
                    and kwargs.get('source') != rule:
                router.forward(interface, frame, rule, kwargs.get('canvas'))
                check = False
        if check:
            if isinstance(packet, dt.ICMP):
                receiver = kwargs.get('receiver')
                icmp = packet.reply()
                icmp.unreachable = True
                reply = dt.Frame(receiver.mac_address, frame.mac_source, icmp)
                receiver.send(reply, kwargs.get('canvas'))


def switch_stp_handler(switch, port, frame, **kwargs):
    if isinstance(frame, dt.STP):
        root_id, bridge_id, path_cost = frame.get_bpdu()
        if root_id < switch.root_id:
            switch.root_id = ro

