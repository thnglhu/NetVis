from network import data as dt
from time import time

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


def static(router, frame, packet, **kwargs):
    for network in router.routing_table:
        rule = router.routing_table[network]
        interface = rule['interface']
        if packet.ip_target in network \
                and packet.ip_target != interface.ip_address \
                and kwargs.get('source') != rule:
            router.forward(interface, frame, rule, kwargs.get('canvas'))
            break
    else:
        if isinstance(packet, dt.ICMP):
            receiver = kwargs.get('receiver')
            icmp = packet.reply()
            icmp.unreachable = True
            reply = dt.Frame(receiver.mac_address, frame.mac_source, icmp)
            receiver.send(reply, kwargs.get('canvas'))


def hub_broadcast_handler(hub, frame, **kwargs):
    source = kwargs.get('source')
    for other in hub.others:
        if other is not source:
            hub.send(frame, other, kwargs.get('canvas'))


def router_forward_handler(router, frame, **kwargs):
    packet = frame.packet
    if packet and kwargs.get('receiver').mac_address == frame.mac_target:
        if router.extend.get('RIP'):

            for network, info in router.extend['RIP']['table'].items():
                if packet.ip_target in network:
                    if info['via'] is None:
                        continue
                    else:
                        rule = {
                            'next_hop': info['via'],
                        }
                        neighbor = router.neighbors.get(str(info['via']))
                        if neighbor:
                            interface = neighbor['via']
                            router.forward(interface, frame, rule, kwargs.get('canvas'))
                        else:
                            continue
                    break
            else:
                static(router, frame, packet, **kwargs)
                # if isinstance(packet, dt.ICMP):
                #     receiver = kwargs.get('receiver')
                #     icmp = packet.reply()
                #     icmp.unreachable = True
                #     reply = dt.Frame(receiver.mac_address, frame.mac_source, icmp)
                #     receiver.send(reply, kwargs.get('canvas'))
        else:
            static(router, frame, packet, **kwargs)
        return True
    return False


def router_hello_handler(router, frame, **kwargs):
    packet = frame.packet
    if packet and isinstance(packet, dt.Hello):
        if packet.is_reply():
            router.neighbors[str(packet.ip_source)] = {
                'ip_address': packet.ip_source,
                'mac_address': frame.mac_source,
                'via': kwargs.get('receiver'),
                'last_time': time(),
            }
        else:
            interface = kwargs.get('receiver')
            frame = packet.reply(interface.ip_address).build(interface.mac_address, frame.mac_source)
            interface.send(frame, kwargs.get('canvas'))
        return True


def router_rip_handler(router, frame, **kwargs):
    packet = frame.packet
    if packet and isinstance(packet, dt.RIP):
        my_table = router.extend['RIP']['table']
        table = packet.table
        for network, rule in table.items():
            if network not in my_table:
                my_table[network] = rule.copy()
                my_table[network]['via'] = packet.ip_source
                my_table[network]['hop'] += 1
            else:
                if my_table[network]['via'] == packet.ip_source or rule['hop'] + 1 < my_table[network]['hop']:
                    my_table[network]['hop'] = rule['hop'] + 1
                    my_table[network]['via'] = packet.ip_source
        return True
    return False
