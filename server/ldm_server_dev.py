import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request
from werkzeug.utils import secure_filename

from server import config as config_server
from server.image_processing.orthophoto import rectify_UCON
from server.image_processing.img_metadata_generation import create_img_metadata_UCON as create_img_metadata
from clients.webodm import WebODM
from clients.mago3d import Mago3D
from server.object_detection.red_tide import detect_red_tide
from server.object_detection.ship_yolo import detect_ship
from drone.drone_image_check import start_image_check

# Initialize flask
app = Flask(__name__)
app.config.from_object(config_server.DJIMavicConfig)

# Initialize multi-thread
executor = ThreadPoolExecutor(2)

# Initialize Mago3D client
mago3d = Mago3D(url=app.config['MAGO3D_CONFIG']['url'], user_id=app.config['MAGO3D_CONFIG']['user_id'],
                        api_key=app.config['MAGO3D_CONFIG']['api_key'])


def allowed_file(fname):
    return '.' in fname and fname.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/project/', methods=['GET', 'POST'])
def project():
    """
    GET : Query project list
    POST : Add a new project
    :return: project_list (GET), project_id (POST)
    """
    if request.method == 'GET':
        project_list = os.listdir(app.config['UPLOAD_FOLDER'])
        return json.dumps(project_list)
    if request.method == 'POST':
        # Create a new project on Mago3D
        res = mago3d.create_project(request.json['name'], request.json['project_type'], request.json['shooting_area'])
        # Mago3D assigns a new project ID to LDM
        project_id = str(res.json()['droneProjectId'])
        # Using the assigned ID, ldm makes a new folder to projects directory
        new_project_dir = os.path.join(app.config['UPLOAD_FOLDER'], project_id)
        os.mkdir(new_project_dir)
        os.mkdir(os.path.join(new_project_dir, 'rectified'))
        # LDM returns the project ID that Mago3D assigned
        return project_id


# 라이브 드론맵: 이미지 업로드, 기하보정 및 가시화
@app.route('/ldm_upload/<project_id_str>', methods=['POST'])
def ldm_upload(project_id_str):
    """
    POST : Input images to the image processing and object detection chain of LDM
    The image processing and object detection chain of LDM covers following procedures.
        1) System calibration
        2) Individual ortho-image generation
        3) Object detection (red tide, ship, etc.)
    :param project_id_str: project_id which Mago3D assigned for each projects
    :return:
    """

    if request.method == 'POST':
        # Initialize variables
        project_folder = os.path.join(app.config['UPLOAD_FOLDER'], project_id_str)
        fname_dict = {'img': None, 'eo': None, 'calibrated_eo': None}

        # 클라이언트로부터 이미지와 EO 파일을 전송받는다
        # 전송된 파일의 무결성을 확인하고 EO 파일에 대해 시스템 칼리브레이션을 수행한다.

        # Check integrity of uploaded files
        for key in ['img', 'eo']:
            if key not in request.files:  # Key check
                return 'No %s part' % key
            file = request.files[key]
            if file.filename == '':  # Value check
                return 'No selected file'
            if file and allowed_file(file.filename):  # If the keys and corresponding values are OK
                fname_dict[key] = secure_filename(file.filename)
                file.save(os.path.join(project_folder, fname_dict[key]))  # 클라이언트로부터 전송받은 파일을 저장한다.
            else:
                return 'Failed to save the uploaded files'

        # IPOD chain 1: System calibration
        if app.config['CALIBRATION']:
            from server.image_processing.apx_file_reader import read_eo_file_UCON
            calibrated_eo = read_eo_file_UCON(os.path.join(project_folder, fname_dict['eo']))
            fname_dict['calibrated_eo'] = fname_dict['eo'].split('.')[0] + '_calibrated.txt'
            with open(os.path.join(project_folder, fname_dict['calibrated_eo']), 'w') as f:
                f.write('%f\t%f\t%f\t%f\t%f\t%f' % (calibrated_eo['lat'], calibrated_eo['lon'], calibrated_eo['alt'], calibrated_eo['omega'], calibrated_eo['phi'], calibrated_eo['kappa']))
        else:
            fname_dict['precalibrated_eo'] = fname_dict['eo'].split('.')[0] + '_precalibrated.txt'
            with open(os.path.join(project_folder, fname_dict['precalibrated_eo']), 'w') as precal_eo_f:
                with open(os.path.join(project_folder, fname_dict['eo']), 'r') as eo_f:
                    eo_f.readline()
                    data = eo_f.readline()
                    precal_eo_f.write(data)

        # TODO: system calibration 실패할 경우 예외처리할 것 (return 'system calibration failed')

        # IPOD chain 2: Individual ortho-image generation
        if app.config['CALIBRATION']:
            eo_key = 'calibrated_eo'
        else:
            eo_key = 'precalibrated_eo'
        rectify_UCON(input_dir=os.path.join(os.getcwd(), 'project\\%s\\' % project_id_str),
                output_dir=os.path.join(os.getcwd(), 'project\\%s\\rectified\\' % project_id_str),
                eo_fname=fname_dict[eo_key],
                img_fname=fname_dict['img'],
                pixel_size=app.config['LDM_CONFIG']['pixel_size'],
                focal_length=app.config['LDM_CONFIG']['focal_length'],
                gsd=app.config['LDM_CONFIG']['gsd'],
                ground_height=app.config['LDM_CONFIG']['ground_height'])

        # 기하보정한 결과(PNG)를 GeoTiff로 변환한다
        fname_dict['img_GTiff'] = fname_dict['img'].split('.')[0] + '.tif'
        os.system('gdal_translate -of GTiff project\\%s\\rectified\\%s project\\%s\\rectified\\%s'
                  % (project_id_str, fname_dict['img'].split('.')[0] + '.png',
                     project_id_str, fname_dict['img_GTiff']))

        # IPOD chain 3: Object detection
        # 적조탐지
        red_tide_result = detect_red_tide('json_template/ldm_mago3d_detected_objects.json',
                       'project\\%s\\rectified\\%s' % (project_id_str, fname_dict['img_GTiff']))
        # 선박탐지
        ship_result = detect_ship('json_template/ldm_mago3d_detected_objects.json',
                       'project\\%s\\rectified\\%s' % (project_id_str, fname_dict['img'].split('.')[0] + '.png'))
        detection_result = red_tide_result + ship_result

        # Generate metadata for Mago3D
        with open(os.path.join('project\\%s\\rectified\\%s' %
                               (project_id_str, fname_dict['eo'].split('.')[0] + '.wkt'))) as f:
            bounding_box_image = f.readline()
            img_metadata = create_img_metadata(img_metadata_json_template_fname='json_template/ldm2mago3d_img_metadata.json',
                                               img_fname=fname_dict['img_GTiff'],
                                               eo_path='project\\%s\\%s' % (project_id_str, fname_dict[eo_key]),
                                               detected_objects=detection_result,
                                               bounding_box_image=bounding_box_image,
                                               drone_project_id=int(project_id_str))

        with open('project\\%s\\rectified\\%s' % (project_id_str, fname_dict['img'].split('.')[0] + '.json'), 'w') as f:
            f.write(json.dumps(img_metadata))

        # Mago3D에 전송
        mago3d = Mago3D(url=app.config['MAGO3D_CONFIG']['url'], user_id=app.config['MAGO3D_CONFIG']['user_id'],
                        api_key=app.config['MAGO3D_CONFIG']['api_key'])
        res = mago3d.upload(img_fname='project\\%s\\rectified\\%s' % (project_id_str, fname_dict['img_GTiff']),
                            img_metadata=img_metadata)

        return 'Image upload and IPOD chain complete'


# 시스템 점검: 드론과의 양방향 통신을 위한 폴링 대기
@app.route('/check/drone_polling')
def check_drone_polling():
    app.config['DRONE']['asked_health_check'] = False
    app.config['DRONE']['asked_sim'] = False
    while True:
        time.sleep(app.config['DRONE']['polling_time'])
        if app.config['DRONE']['asked_health_check']:
            return 'START_HEALTH_CHECK'
        elif app.config['DRONE']['asked_sim']:
            return app.config['SIMULATION_ID']


@app.route('/check/drone_checklist_result')
def check_drone_result():
    app.config['DRONE']['checklist_result'] = 'OK'
    return 'OK'


@app.route('/check/drone')
def check_drone():
    app.config['DRONE']['asked_health_check'] = True
    time.sleep(app.config['DRONE']['timeout'])
    if app.config['DRONE']['checklist_result'] == 'OK':
        app.config['DRONE']['checklist_result'] = 'None'
        return 'OK'
    else:
        return 'DISCONNECTED_OR_NOT_RESPONDING'


@app.route('/check/beacon')
def check_beacon():
    return 'OK'


@app.route('/check/sim/from_ldm')
def check_sim_from_ldm():
    app.config['SIMULATION_ID'] = request.args.get('simulation_id')
    executor.submit(start_image_check, app.config['SIMULATION_ID'])
    return 'OK'


@app.route('/check/sim/from_drone')
def check_sim_from_drone():
    app.config['SIMULATION_ID'] = request.args.get('simulation_id')
    app.config['DRONE']['asked_sim'] = True
    return 'OK'


# 오픈드론맵: 후처리
@app.route('/webodm_upload/start_processing/<project_id>')
def webodm_start_processing(project_id_str):
    webodm = WebODM(
        url=app.config['WEBODM_CONFIG']['url'],
        username=app.config['WEBODM_CONFIG']['username'],
        password=app.config['WEBODM_CONFIG']['password']
    )
    webodm.create_project(project_name=project_id_str)
    project_folder = 'project/' + project_id_str
    webodm.create_task(project_folder)

    return 'ODM'



if __name__ == '__main__':
    app.run(threaded=True, host='192.168.0.75')
