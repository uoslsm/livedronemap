from clients.ldm_client import Livedronemap
import time
import glob
from tqdm import tqdm

img_fname_list = glob.glob('example_dji_red-tide-detection/*.JPG')

ldm = Livedronemap('http://127.0.0.1:5000/')
project_id = ldm.create_project('test_dji_red_tide_detection_200')
ldm.set_current_project(project_id)

for img_fname in tqdm(img_fname_list):
    eo_fname = img_fname.split('.')[0] + '.txt'
    result = ldm.ldm_upload(img_fname, eo_fname)
    if result.status_code != 200:
        print('Image: %s, EO: %s, Result: %s' % (img_fname, eo_fname, result.status_code))
    time.sleep(1)
