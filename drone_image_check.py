import json
import time
import glob
from tqdm import tqdm

from config_drone import BaseConfig as Config
from clients.ldm_client import Livedronemap
from clients.mago3d import Mago3D

MAGO3D_CONFIG = json.load(open('config_mago3d.json', 'r'))


def start_image_check(simulation_id_str=None):
    img_fname_list = glob.glob('%s/*.JPG' % Config.DIRECTORY_IMAGE_CHECK)

    # 현재 프로젝트 설정
    ldm = Livedronemap(Config.LDM_ADDRESS, Config.MAGO3D_ADDRESS)
    drone_project_id = ldm.create_project('This is for test', project_type='1')
    ldm.set_current_project(drone_project_id)

    # Mago3D 클라이언트 설정
    mago3d = Mago3D(url=MAGO3D_CONFIG['url'], user_id=MAGO3D_CONFIG['user_id'],
                    api_key=MAGO3D_CONFIG['api_key'])

    # 프로젝트 생성 후 프로젝트 ID 연결
    mago3d.set_simulation_id(simulation_id_str, drone_project_id, status='2')

    # 테스트 데이터 전송
    for img_fname in tqdm(img_fname_list):
        eo_fname = img_fname.split('.')[0] + '.txt'
        result = ldm.ldm_upload(img_fname, eo_fname)
        if result.status_code != 200:
            print('Image: %s, EO: %s, Result: %s' % (img_fname, eo_fname, result.status_code))
            mago3d.set_simulation_id(simulation_id_str, drone_project_id, status='1')
            return 0
        time.sleep(1)

    # 전송 성공시 '성공' 표시로 전환
    mago3d.conclude_simulation(drone_project_id)


if __name__ == '__main__':
    start_image_check()