import json
from abc import *


class BaseConfig(object, metaclass=ABCMeta):
    DEBUG = False
    TESTING = False
    UPLOAD_FOLDER = 'project'
    ALLOWED_EXTENSIONS = set(['JPG', 'jpg', 'txt'])
    WEBODM_CONFIG = json.load(open('config_webodm.json', 'r'))
    MAGO3D_CONFIG = json.load(open('config_mago3d.json', 'r'))
    PATH = {
        'img_metadata_path': 'json_templates/ldm2mago3d_img_metadata.json',
        'gdal_path': 'C:\\OSGeo4W64\\bin\\gdal_translate.exe'
    }
    SIMULATION_ID = None
    CALIBRATION = True

