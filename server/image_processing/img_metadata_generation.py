import arrow


def create_img_metadata(drone_project_id, data_type, file_name, detected_objects, drone_id, drone_name, parsed_eo):
    img_metadata = {
        "drone_project_id": drone_project_id,
        "data_type": data_type,
        "file_name": file_name,
        "detected_objects": detected_objects,
        "drone": {
            "drone_id": drone_id,
            "drone_name": drone_name,
            "latitude": parsed_eo[0],
            "longitude": parsed_eo[1],
            "altitude": parsed_eo[2],
            "roll": parsed_eo[3],
            "pitch": parsed_eo[4],
            "yaw": parsed_eo[5],
            "insert_date": arrow.utcnow().format('YYYYMMDDHHmmss')
        },
        # TODO: EXIF 데이터에서 시간 추출 (지금은 그냥 현재시각으로)
        "shooting_date": arrow.utcnow().format('YYYYMMDDHHmmss')
    }

    return img_metadata
