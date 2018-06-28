from flask import Flask, request
from werkzeug.utils import secure_filename
import os, json
from orthophoto.orthophoto import ortho_rectify

UPLOAD_FOLDER = 'project'
ALLOWED_EXTENSIONS = set(['jpg', 'txt'])

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
            os.mkdir(os.path.join(new_project_dir, 'raw'))
            os.mkdir(os.path.join(new_project_dir, 'rectified'))
            return 'Project folder %s created' % new_project_name


# 라이브 드론맵: 이미지 업로드, 기하보정 및 가시화
@app.route('/ldm_upload/<project_name>', methods=['POST'])
def ldm_upload(project_name):
    project_folder = os.path.join(app.config['UPLOAD_FOLDER'], project_name)
    project_raw_folder = os.path.join(project_folder, 'raw')

    if request.method == 'POST':
        # 클라이언트로부터 이미지와 EO 파일을 전송받는다.
        fname_dict = {'img': None, 'eo': None}
        for key in list(fname_dict.keys()):
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
                file.save(os.path.join(project_raw_folder, filename))

                if key == 'eo':
                    # 전송받은 파일이 EO인 경우 시스템 칼리브레이션을 수행한다.
                    from apx_file_reader import read_eo_file
                    calibrated_eo = read_eo_file(fname_dict['eo'])

                    # TODO: 전송받은 이미지와 조정한 EO를 기하보정한다.
                    '''
                    ortho_rectify(input_file_path_tmp="D:\\python-workspace\\livedronemap\\orthophoto\\workspace\\",
                                  output_file_path_tmp="D:\\python-workspace\\livedronemap\\orthophoto\\workspace\\result\\",
                                  eo_name_tmp="2017-04-10_125832.txt",
                                  image_name_tmp="2017-04-10_125832.jpg",
                                  pixel_size=0.000006,
                                  focal_length=0.035,
                                  gsd=0.10,
                                  ground_height=23)
                    '''
                    # TODO: 기하보정한 이미지를 가시화 모듈에 전달한다.

                    return str(calibrated_eo['lat'])


# 오픈드론맵: 항공삼각측량
@app.route('/odm_upload/<project_name>', methods=['POST'])
def odm_upload(project_name):
    # TODO: WebODM에 데이터셋을 업로드한다.
    return 'ODM'


if __name__ == '__main__':
    app.run()
