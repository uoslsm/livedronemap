import json
import os
import time

from flask import Flask, request
from werkzeug.utils import secure_filename

import config_server
from image_processing.orthophoto import rectify

# 플라스크 초기화
app = Flask(__name__)
app.config.from_object(config_server.KrihsConfig)


def allowed_file(fname):
    return '.' in fname and fname.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# 프로젝트 관리
@app.route('/project/', methods=['GET', 'POST'])
def project():
    project_list = os.listdir(app.config['UPLOAD_FOLDER'])
    if request.method == 'GET':
        return json.dumps(project_list)
    if request.method == 'POST':
        new_project_name = request.json['name']
        if new_project_name in project_list:
            return 'Project folder %s already exists' % new_project_name
        else:
            new_project_dir = os.path.join(app.config['UPLOAD_FOLDER'], new_project_name)
            os.mkdir(new_project_dir)
            os.mkdir(os.path.join(new_project_dir, 'rectified'))
            return 'Project folder %s created' % new_project_name


# 라이브 드론맵: 이미지 업로드, 기하보정 및 가시화
@app.route('/ldm_upload/<project_name>', methods=['POST'])
def ldm_upload(project_name):
    project_folder = os.path.join(app.config['UPLOAD_FOLDER'], project_name)
    if request.method == 'POST':
        # 클라이언트로부터 이미지와 EO 파일을 전송받는다. 전송된 파일의 무결성을 확인하고 EO 파일에 대해 시스템 칼리브레이션을 수행한다.
        fname_dict = {'img': None, 'eo': None, 'calibrated_eo': None}
        for key in ['img', 'eo']:
            if key not in request.files:  # 전송받은 파일의 상태 확인: 이미지나 EO 중 하나의 키가 빠진 경우
                return 'No %s part' % key
            file = request.files[key]
            if file.filename == '':  # 전송받은 파일의 상태 확인: 키는 둘 다 있는데 값이 없는 경우
                return 'No selected file'
            if file and allowed_file(file.filename):  # 전송받은 파일의 상태 확인: 키와 값이 모두 정상이고 허용된 확장자일 경우
                filename = secure_filename(file.filename)
                fname_dict[key] = filename
                file.save(os.path.join(project_folder, filename))  # 클라이언트로부터 전송받은 파일을 저장한다.
                if key == 'eo': # 전송받은 파일이 EO인 경우, 그리고 칼리브레이션 모드가 켜진 경우 시스템 칼리브레이션을 수행한다.
                    if app.config['CALIBRATION']:
                        from image_processing.apx_file_reader import read_eo_file
                        calibrated_eo = read_eo_file(os.path.join(project_folder, fname_dict['eo']))
                        fname_dict['calibrated_eo'] = fname_dict['eo'].split('.')[0] + '_calibrated.txt'
                        with open(os.path.join(project_folder, fname_dict['calibrated_eo']), 'w') as f:
                            f.write('%f\t%f\t%f\t%f\t%f\t%f' % (calibrated_eo['lat'], calibrated_eo['lon'], calibrated_eo['alt'], calibrated_eo['omega'], calibrated_eo['phi'], calibrated_eo['kappa']))
        if fname_dict != {'img': None, 'eo': None, 'calibrated_eo': None}:  # 전송받은 이미지와 조정한 EO를 기하보정한다.
            if app.config['CALIBRATION']:
                eo_key = 'calibrated_eo'
            else:
                eo_key = 'eo'
            rectify(input_dir=os.path.join(os.getcwd(), 'project\\%s\\' % project_name),
                    output_dir=os.path.join(os.getcwd(), 'project\\%s\\rectified\\' % project_name),
                    eo_fname=fname_dict[eo_key],
                    img_fname=fname_dict['img'],
                    pixel_size=app.config['LDM_CONFIG']['pixel_size'],
                    focal_length=app.config['LDM_CONFIG']['focal_length'],
                    gsd=app.config['LDM_CONFIG']['gsd'],
                    ground_height=app.config['LDM_CONFIG']['ground_height'])

        # TODO: 기하보정한 이미지를 가시화 모듈에 전달한다.

        return 'LDM'


# 시스템 점검: 드론과의 양방향 통신을 위한 폴링 대기
@app.route('/check/drone_poling')
def check_drone_polling():
    app.config['DRONE']['asked_to_check'] = False
    while True:
        time.sleep(app.config['DRONE']['polling_time'])
        if app.config['DRONE']['asked_to_check']:
            return 'START_CHECKLIST'


@app.route('/check/drone_checklist_result')
def check_drone_result():
    app.config['DRONE']['checklist_result'] = 'OK'
    return 'OK'


@app.route('/check/drone')
def check_drone():
    app.config['DRONE']['asked_to_check'] = True
    time.sleep(app.config['DRONE']['timeout'])
    if app.config['DRONE']['checklist_result'] == 'OK':
        app.config['DRONE']['checklist_result'] = 'None'
        return 'OK'
    else:
        return 'DISCONNECTED_OR_NOT_RESPONDING'


# 오픈드론맵: 후처리
@app.route('/odm_upload/<project_name>', methods=['POST'])
def odm_upload(project_name):
    # TODO: WebODM에 데이터셋을 업로드한다.
    return 'ODM'


if __name__ == '__main__':
    app.run(threaded=True)
