import json
import arrow


def create_img_metadata(img_metadata_json_template_fname, img_fname, eo_path, detected_objects=[],
                        drone_project_id=1, data_type=0, drone_id=0, drone_name='test_drone'):
    img_metadata = json.load(open(img_metadata_json_template_fname, 'r'))
    img_metadata['drone_project_id'] = drone_project_id
    img_metadata['data_type'] = data_type
    img_metadata['file_name'] = img_fname
    img_metadata['detected_objects'] = detected_objects
    with open(eo_path, 'r') as f:
        eo = f.readline().split('\t')
        img_metadata['drone']['latitude'] = float(eo[2])
        img_metadata['drone']['longitude'] = float(eo[1])
        img_metadata['drone']['altitude'] = float(eo[3])
        img_metadata['drone']['roll'] = float(eo[4])
        img_metadata['drone']['pitch'] = float(eo[5])
        img_metadata['drone']['yaw'] = float(eo[6])
        # TODO: EXIF 데이터에서 시간 추출 (지금은 그냥 현재시각으로)
        img_metadata['drone']['insert_date'] = arrow.utcnow().format('YYYYMMDDHHmmss')
    img_metadata['shooting_date'] = arrow.utcnow().format('YYYYMMDDHHmmss')
    return img_metadata
