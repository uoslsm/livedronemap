import json
import time
import glob
from tqdm import tqdm
import numpy as np
import arrow

from drone.config import BaseConfig as Config
from clients.ldm_client import Livedronemap
from clients.mago3d import Mago3D

MAGO3D_CONFIG = json.load(open('drone/config_mago3d.json', 'r'))


def start_image_check(simulation_id_str=None):
    img_fname_list = glob.glob('%s/*.JPG' % Config.DIRECTORY_IMAGE_CHECK)

    # 현재 프로젝트 설정
    ldm = Livedronemap(Config.LDM_ADDRESS)
    drone_project_id = ldm.create_project('Simulation (%s)' % arrow.utcnow().format('YYYYMMDDHHmmss'), project_type='0')  # TODO: project_type SHOULD BE '1'
    ldm.set_current_project(drone_project_id)

    # Mago3D 클라이언트 설정
    mago3d = Mago3D(url=MAGO3D_CONFIG['url'], user_id=MAGO3D_CONFIG['user_id'],
                    api_key=MAGO3D_CONFIG['api_key'])

    # 프로젝트 생성 후 프로젝트 ID 연결
    mago3d.set_simulation_id(simulation_id_str, drone_project_id, status='2')

    res_time_list = []
    # 테스트 데이터 전송
    for img_fname in tqdm(img_fname_list):
        start_time = time.time()
        eo_fname = img_fname.split('.')[0] + '.txt'

        upload_start_time = time.time()

        result = ldm.ldm_upload(img_fname, eo_fname)
        if result.status_code != 200:
            print('Image: %s, EO: %s, Result: %s' % (img_fname, eo_fname, result.status_code))
            print(result)
            mago3d.set_simulation_id(simulation_id_str, drone_project_id, status='1')
            return 0

        f = open("log.txt", 'a')
        cur_time = "%s\t%f\n" % (img_fname, upload_start_time)
        f.write(cur_time)

        end_time = time.time()
        res_time = end_time - start_time
        res_time_list.append(res_time)
        time.sleep(Config.UPLOAD_INTERVAL)

    # 전송 성공시 '성공' 표시로 전환
    print(mago3d.conclude_simulation(drone_project_id))

    # 전송시간 출력
    print('Average Time: %f, Std: %s' % (np.mean(res_time_list), np.std(res_time_list)))


if __name__ == '__main__':
    start_image_check()
