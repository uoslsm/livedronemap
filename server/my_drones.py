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
            'gsd': 'auto',
            'ground_height': 27.0,
            "R_CB": np.array(
                [[0.997391604272809, -0.0193033671589004, -0.0695511879297631],
                 [0.0115400822765142, 0.993826984996126, -0.110339251377565],
                 [0.0712517664845147, 0.109248816514592, 0.991457453380122]], dtype=float)
        }
        self.pre_calibrated = pre_calibrated

    def preprocess_eo_file(self, eo_path):
        eo_line = np.genfromtxt(
            eo_path,
            delimiter='\t',
            dtype={
                'names': ('Image', 'Longitude', 'Latitude', 'Altitude', 'Yaw', 'Pitch', 'Roll'),
                'formats': ('U15', '<f8', '<f8', '<f8', '<f8', '<f8', '<f8')
            }
        )

        eo_line['Roll'] = eo_line['Roll'] * math.pi / 180
        eo_line['Pitch'] = eo_line['Pitch'] * math.pi / 180
        eo_line['Yaw'] = eo_line['Yaw'] * math.pi / 180

        parsed_eo = [float(eo_line['Longitude']), float(eo_line['Latitude']), float(eo_line['Altitude']),
                     float(eo_line['Roll']), float(eo_line['Pitch']), float(eo_line['Yaw'])]

        return parsed_eo


class DJIPhantom4RTK(BaseDrone):
    def __init__(self, pre_calibrated=False):
        self.ipod_params = {
            "sensor_width": 6.3,
            'focal_length': 0.0088,
            'gsd': 'auto',
            'ground_height': 27.0,
            "R_CB": np.array(
                [[0.992103011532570, -0.0478682839576757, -0.115932057253170],
                 [0.0636038625107261, 0.988653550290218, 0.136083452970098],
                 [0.108102558627082, -0.142382530141501, 0.983890772356761]], dtype=float)
        }
        self.pre_calibrated = pre_calibrated

    def preprocess_eo_file(self, eo_path):
        eo_line = np.genfromtxt(
            eo_path,
            delimiter='\t',
            dtype={
                'names': ('Image', 'Longitude', 'Latitude', 'Altitude', 'Yaw', 'Pitch', 'Roll'),
                'formats': ('U15', '<f8', '<f8', '<f8', '<f8', '<f8', '<f8')
            }
        )

        eo_line['Roll'] = eo_line['Roll'] * math.pi / 180
        eo_line['Pitch'] = eo_line['Pitch'] * math.pi / 180
        eo_line['Yaw'] = eo_line['Yaw'] * math.pi / 180

        parsed_eo = [float(eo_line['Longitude']), float(eo_line['Latitude']), float(eo_line['Altitude']),
                     float(eo_line['Roll']), float(eo_line['Pitch']), float(eo_line['Yaw'])]

        return parsed_eo


class TiLabETRI(BaseDrone):
    def __init__(self, pre_calibrated=False):
        self.ipod_params = {
            "sensor_width": 23.5,
            "focal_length": 0.0016,
            "gsd": 0.25,
            "ground_height": 27.0,
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
