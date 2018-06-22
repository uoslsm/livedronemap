from flask import Flask, request
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(fname):
    return '.' in fname and fname.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/ldm_upload/', methods=['POST'])
def ldm_upload():
    if request.method == 'POST':
        # 클라이언트로부터 이미지와 EO 파일을 전송받는다.
        fname_dict = {
            'img': None,
            'eo': None
        }
        for key in list(fname_dict.keys()):
            if key not in request.files:
                return 'No %s part' % key
            file = request.files[key]
            if file.filename == '':
                return 'No selected file'
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                fname_dict[key] = filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # 전송받은 EO 파일을 이용하여 시스템 칼리브레이션을 수행한다.
        from apx_file_reader import read_eo_file
        calibrated_eo = read_eo_file(fname_dict['eo'])

        print(calibrated_eo)

        return str(calibrated_eo['lat'])



@app.route('/odm_upload', methods=['POST'])
def odm_upload():
    return 0


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
