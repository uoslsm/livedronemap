import requests
from drone.config import BaseConfig as Config
from drone.drone_image_check import start_image_check

while True:
    print('Polling connection...')

    # LDM과 드론을 연결한 후 대기(폴링 기법), 가시화 모듈에서 요청을 보내면(START_CHECKLIST) 체크리스트 수행
    result = requests.get(Config.LDM_ADDRESS + 'check/drone_polling')

    if result.text == 'START_HEALTH_CHECK':
        print('[START_HEALTH_CHECK] LDM asked me to start checklist')
        print('[START_HEALTH_CHECK] Everything is OK')
        requests.get(Config.LDM_ADDRESS + 'check/drone_checklist_result')
    else:
        simulation_id_str = result.text
        print('[START_SIM] simulation_id: %s' % result.text)
        start_image_check(simulation_id_str=simulation_id_str)
