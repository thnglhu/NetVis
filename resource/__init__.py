from PIL import ImageTk, Image
__image_paths = dict()
__image_paths['hub'] = "resource/images/hub.png"
__image_paths['pc-on'] = "resource/images/pc-on.png"
__image_paths['pc-off'] = "resource/images/pc-off.png"
__image_paths['router'] = "resource/images/router.png"
__image_paths['switch'] = "resource/images/switch.png"

__image_photo = dict()


def get_image(name):
    __image_photo[name] = __image_photo.get(name, ImageTk.PhotoImage(file=__image_paths[name]))
    return __image_photo[name]
