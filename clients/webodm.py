"""
Refer to:
https://github.com/OpenDroneMap/WebODM/blob/master/slate/examples/process_images.py
"""

import requests
import os


class WebODM:
    def __init__(self, url, username, password):
        self.url = url
        res = requests.post(
            url=self.url + 'api/token-auth/',
            data={'username': username, 'password': password}
        ).json()
        self.token = res['token']
        self.project_name = None
        self.project_id = None
        self.task_id = None

    def create_project(self, project_name):
        self.project_name = project_name
        res = requests.post(
            url=self.url + 'api/projects/',
            headers={'Authorization': 'JWT {}'.format(self.token)},
            data={'name': self.project_name}
        ).json()
        self.project_id = res['id']

    def create_task(self, project_folder):
        image_list = []
        image_fname_list = os.listdir(project_folder)
        for image_fname in image_fname_list:
            image_list.append(
                ('images', (image_fname, open(os.path.join(project_folder, image_fname), 'rb'), 'image/jpg'))
            )
        url_task = self.url + 'api/projects/{}/tasks/'
        res = requests.post(
            url=url_task.format(self.project_id),
            headers={'Authorization': 'JWT {}'.format(self.token)},
            files=image_list
        ).json()
        self.task_id = res['id']
