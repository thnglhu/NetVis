from .host import Host
from .switch import Switch
from .hub import Hub
from .router import Router

classification = {
    'host': Host,
    'hub': Hub,
    'switch': Switch,
    'router': Router
}
