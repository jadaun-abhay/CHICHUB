from django.conf import settings


def check_image_validity(images):
    for image in images:
        img_extension = image.name.split('.')[-1]
        img_content_type = image.content_type
        if img_extension not in settings.WHITELISTED_IMAGES.keys():
            response = {
                'file': image.name,
                'msg': 'Image type not supported (must be .jpg, .png or .jpeg)',
            }
            return response
        elif img_content_type not in settings.WHITELISTED_IMAGES.values():
            response = {
                'file': image.name,
                'msg': 'Image type not supported',
            }
            return response
    return True


def encode(string):
    encoded_string = bin(string)[2:].replace('0', 'A').replace('1', 'B')
    return encoded_string


def decode(string):
    decoded_string = int('0b' + string.replace('A', '0').replace('B', '1'), 2)
    return decoded_string
