from abc import *
import math
import numpy as np


class BaseDrone(metaclass=ABCMeta):
    polling_config = {
        'asked_health_check': False,
        'asked_sim': False,
        'checklist_result': None,
        'polling_time': 0.5,
        'timeout': 10
    }

    @abstractmethod
    def preprocess_eo_file(self, eo_path):
        """
        This abstract function parses a given EO file and returns parsed_eo (see below).
        It SHOULD BE implemented for each drone classes.

        An example of parsed_eo
        parsed_eo = [latitude, longitude, altitude, omega, phi, kappa]
        Unit of omega, phi, kappa: radian
        """
        pass

    # @abstractmethod
    def calibrate_initial_eo(self):
        pass


class DJIMavic(BaseDrone):
    def __init__(self, pre_calibrated=False):
        self.ipod_params = {
            "sensor_width": 6.3,
            'focal_length': 0.0047,
            'gsd': 0.25,
            'ground_height': 0.65
        }
        self.pre_calibrated = pre_calibrated

    def preprocess_eo_file(self, eo_path):
        eo_line = np.genfromtxt(
            eo_path,
            delimiter='\t',
            dtype={
                'names': ('Image', 'Longitude', 'Latitude', 'Altitude', 'Omega', 'Phi', 'Kappa'),
                'formats': ('U15', '<f8', '<f8', '<f8', '<f8', '<f8', '<f8')
            }
        )

        eo_line['Omega'] = eo_line['Omega'] * math.pi / 180
        eo_line['Phi'] = eo_line['Phi'] * math.pi / 180
        eo_line['Kappa'] = eo_line['Kappa'] * math.pi / 180

        parsed_eo = [float(eo_line['Longitude']), float(eo_line['Latitude']), float(eo_line['Altitude']),
                     float(eo_line['Omega']), float(eo_line['Phi']), float(eo_line['Kappa'])]

        return parsed_eo


class TiLabETRI(BaseDrone):
    def __init__(self, pre_calibrated=False):
        self.ipod_params = {
            "sensor_width": 23.5,
            "focal_length": 0.0016,
            "gsd": 0.25,
            "ground_height": 33.35
        }
        self.pre_calibrated = pre_calibrated

    def preprocess_eo_file(self, eo_path):
        with open(eo_path, 'r') as f:
            data = f.readline().split(' ')
            lat = data[1].split('=')[1]
            lon = data[2].split('=')[1]
            alt = data[3].split('=')[1]
            kappa = (float(data[6].split('=')[1]) + 90.0) * math.pi / 180
            parsed_eo = [float(lon), float(lat), float(alt), 0.0, 0.0, float(kappa)]

            return parsed_eo
