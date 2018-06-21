from flask import Flask, request
import json, time

app = Flask(__name__)


@app.route('/ldm_upload_data', methods=['POST'])
def ldm_upload_data():
    if request.method == 'POST':
        data = request.get_json()
        data = json.loads(data) #Decode JSON: JSON->Dictionary
        result = {'status': 'OK', 'result': data['x_w'] + data['y_w']}
        time.sleep(10)

        '''
        f_img = 이미지 파일
        f_txt = 텍스트 파일
        텍스트 파일 파싱
        원하는 변수만 추출
        시스템 칼리브레이션 R 곱하기
        기하보정 프로그램에 조정된 EO와 이미지 파일, 기타 파라미터를 넣고 실행시키기 
        '''

        return json.dumps(result)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
