import tensorflow


def top_k(*args, **kwargs):
    return tensorflow.nn.top_k(*args, **kwargs)


def non_max_suppression(*args, **kwargs):
    return tensorflow.image.non_max_suppression(*args, **kwargs)


def gather_nd(*args, **kwargs):
    return tensorflow.gather_nd(*args, **kwargs)


def pad(*args, **kwargs):
    return tensorflow.pad(*args, **kwargs)


def where(*args, **kwargs):
    return tensorflow.where(*args, **kwargs)


def map_fn(*args, **kwargs):
    return tensorflow.map_fn(*args, **kwargs)


def clip_by_value(*args, **kwargs):
    return tensorflow.clip_by_value(*args, **kwargs)


def meshgrid(*args, **kwargs):
    return tensorflow.meshgrid(*args, **kwargs)


def resize_images(images, size, method='bilinear', align_corners=False):
    methods = {
        'bilinear': tensorflow.image.ResizeMethod.BILINEAR,
        'nearest' : tensorflow.image.ResizeMethod.NEAREST_NEIGHBOR,
        'bicubic' : tensorflow.image.ResizeMethod.BICUBIC,
        'area'    : tensorflow.image.ResizeMethod.AREA,
    }
    return tensorflow.image.resize_images(images, size, methods[method], align_corners)
