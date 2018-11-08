import json


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    UPLOAD_FOLDER = 'project'
    ALLOWED_EXTENSIONS = set(['JPG', 'jpg', 'txt'])
    DRONE = {
        'asked_health_check': False,
        'asked_sim': False,
        'checklist_result': None,
        'polling_time': 0.5,
        'timeout': 10
    }
    WEBODM_CONFIG = json.load(open('config_webodm.json', 'r'))
    MAGO3D_CONFIG = json.load(open('config_mago3d.json', 'r'))
    PATH = {
        'img_metadata_path': 'json_templates/ldm2mago3d_img_metadata.json',
        'gdal_path': 'C:\\OSGeo4W64\\bin\\gdal_translate.exe'
    }


class KrihsConfig(BaseConfig):
    CALIBRATION = True
    LDM_CONFIG = {
        "pixel_size": 0.00000488967,
        'focal_length': 0.025,
        'gsd': 0.25,
        'ground_height': 10
    }


class DJIMavicConfig(BaseConfig):
    CALIBRATION = False
    LDM_CONFIG = {
        "pixel_size": 0.00000156425,
        'focal_length': 0.0047,
        'gsd': 0.25,
        'ground_height': 0
    }
