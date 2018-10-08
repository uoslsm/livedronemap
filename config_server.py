class BaseConfig(object):
    DEBUG = False
    TESTING = False
    UPLOAD_FOLDER = 'project'
    ALLOWED_EXTENSIONS = set(['JPG', 'jpg', 'txt'])
    DRONE = {
        'asked_to_check': False,
        'checklist_result': None,
        'polling_time': 0.5,
        'timeout': 10
    }


class KrihsConfig(BaseConfig):
    CALIBRATION = True
    LDM_CONFIG = {
        "pixel_size": 0.00000488967,
        'focal_length': 0.025,
        'gsd': 0.25,
        'ground_height': 10
    }