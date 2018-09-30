class BaseConfig(object):
    DEBUG = False
    TESTING = False
    UPLOAD_FOLDER = 'project'
    ALLOWED_EXTENSIONS = set(['JPG', 'jpg', 'txt'])


class KhrisConfig(BaseConfig):
    CALIBRATION = True
    LDM_CONFIG = {
        "pixel_size": 0.00000488967,
        'focal_length': 0.025,
        'gsd': 0.25,
        'ground_height': 10
    }


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True