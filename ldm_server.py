from flask import Flask, request
from werkzeug.utils import secure_filename
import os
import json
from utils.orthophoto import rectify

UPLOAD_FOLDER = 'project'
ALLOWED_EXTENSIONS = set(['JPG', 'jpg', 'txt'])
CALIBRATION = False

# 플라스크 초기화
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(fname):
    return '.' in fname and fname.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        # 클라이언트로부터 이미지와 EO 파일을 전송받는다.
        fname_dict = {'img': None, 'eo': None, 'calibrated_eo': None}

        # 전송된 파일의 무결성을 확인하고 EO 파일에 대해 시스템 칼리브레이션을 수행한다.
        for key in ['img', 'eo']:
            # 전송받은 파일의 상태 확인: 이미지나 EO 중 하나의 키가 빠진 경우
            if key not in request.files:
                return 'No %s part' % key
            file = request.files[key]
            # 전송받은 파일의 상태 확인: 키는 둘 다 있는데 값이 없는 경우
            if file.filename == '':
                return 'No selected file'
            # 전송받은 파일의 상태 확인: 키와 값이 모두 정상이고 허용된 확장자일 경우
            if file and allowed_file(file.filename):
                # 클라이언트로부터 전송받은 파일을 저장한다.
                filename = secure_filename(file.filename)
                fname_dict[key] = filename
                file.save(os.path.join(project_folder, filename))
                if key == 'eo':
                    # 전송받은 파일이 EO인 경우, 그리고 칼리브레이션 모드가 켜진 경우 시스템 칼리브레이션을 수행한다.
                    if CALIBRATION:
                        from apx_file_reader import read_eo_file
                        calibrated_eo = read_eo_file(fname_dict['eo'])
                        fname_dict['calibrated_eo'] = fname_dict['eo'].split('.')[0] + '_calibrated.txt'
                        with open(os.path.join(project_folder, fname_dict['calibrated_eo']), 'w') as f:
                            f.write('%f\t%f\t%f\t%f\t%f\t%f' % (calibrated_eo['lat'], calibrated_eo['lon'], calibrated_eo['alt'], calibrated_eo['omega'], calibrated_eo['phi'], calibrated_eo['kappa']))

        # 전송받은 이미지와 조정한 EO를 기하보정한다.
        if fname_dict != {'img': None, 'eo': None, 'calibrated_eo': None}:
            if CALIBRATION:
                eo_key = 'calibrated_eo'
            else:
                eo_key = 'eo'
            rectify(input_dir="D:\\python-workspace\\livedronemap\\project\\%s\\" % project_name,
                    output_dir="D:\\python-workspace\\livedronemap\\project\\%s\\rectified\\" % project_name,
                    eo_fname=fname_dict[eo_key],
                    img_fname=fname_dict['img'],
                    pixel_size=0.00000156192,
                    focal_length=0.00361,
                    gsd=0.25,
                    ground_height=355)

        # TODO: 기하보정한 이미지를 가시화 모듈에 전달한다.

        return 'LDM'


# 오픈드론맵: 항공삼각측량
@app.route('/odm_upload/<project_name>', methods=['POST'])
def odm_upload(project_name):
    # TODO: WebODM에 데이터셋을 업로드한다.
    return 'ODM'


if __name__ == '__main__':
    # app.run()
    socket_io.run(app)