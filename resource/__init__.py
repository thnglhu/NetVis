from PIL import ImageTk, Image
image_paths = dict()
image_paths['hub'] = "resource/images/hub.png"
image_paths['pc-on'] = "resource/images/pc-on.png"
image_paths['pc-on-focus'] = "resource/images/pc-on-focus.png"
image_paths['pc-off'] = "resource/images/pc-off.png"
image_paths['router'] = "resource/images/router.png"
image_paths['switch'] = "resource/images/switch.png"

image_photo = dict()


def get_image(name):
    image_photo[name] = image_photo.get(name, ImageTk.PhotoImage(file=image_paths[name]))
    return image_photo[name]
