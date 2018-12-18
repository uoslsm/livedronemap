import json
import arrow
from object_detection.lib.ship_yolo.object_detection_yolo import start_ship_detection

def detect_ship(json_template_fname, input_png_path):
    input_pgw_path = input_png_path.split('.')[0] + '.pgw'
    with open(input_pgw_path, 'r') as f:
        data = f.readlines()
        geom_info = {
            'gsd': {
                'x': float(data[0]),
                'y': float(data[3])
            },
            'ul': {
                'x': float(data[4]),
                'y': float(data[5])
            }
        }
    geom_boxes = start_ship_detection(input_png_path, geom_info)
    for number, geom_box in enumerate(geom_boxes):
        geometry = 'POINT (%f %f)' % (geom_box['center']['x'], geom_box['center']['y'])
        bounding_box_geometry = 'POLYGON ((%f %f, %f %f, %f %f, %f %f))' % (
            geom_box['bounding_box']['coord_1']['x'],
            geom_box['bounding_box']['coord_1']['y'],
            geom_box['bounding_box']['coord_2']['x'],
            geom_box['bounding_box']['coord_2']['y'],
            geom_box['bounding_box']['coord_3']['x'],
            geom_box['bounding_box']['coord_3']['y'],
            geom_box['bounding_box']['coord_4']['x'],
            geom_box['bounding_box']['coord_4']['y']
        )
        detected_objects_list = []
        detected_objects = json.load(open(json_template_fname, 'r'))
        detected_objects['number'] = number
        detected_objects['object_type'] = '0'  # 0: 선박탐지, 1: 기름유출
        detected_objects['geometry'] = geometry
        detected_objects['bounding_box_geometry'] = bounding_box_geometry
        detected_objects['detected_date'] = arrow.utcnow().format('YYYYMMDDHHmmss')
        detected_objects['insert_date'] = arrow.utcnow().format('YYYYMMDDHHmmss')
        detected_objects_list.append(detected_objects)
    return detected_objects_list


if __name__ == '__main__':
    detect_ship(json_template_fname=None, input_png_path='test.png')