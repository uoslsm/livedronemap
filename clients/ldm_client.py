import requests


class Livedronemap:
    def __init__(self, url):
        self.url = url
        self.current_project_id = None

    def create_project(self, project_name, project_type='0'):
        project_json = {
            'mode': 'create',
            'name':  project_name,
            'project_type': project_type
        }
        r = requests.post(self.url + 'project/', json=project_json)
        return r.text

    def read_project(self):
        r = requests.get(self.url + 'project/')
        return r.json()

    def set_current_project(self, project_id):
        existing_projects = self.read_project()
        if project_id in existing_projects:
            self.current_project_id = project_id
        else:
            print('Project %s does not exist' % project_id)

    def ldm_upload(self, img_fname, eo_fname):
        if self.current_project_id is not None:
            try:
                files = {
                    'img': open(img_fname, 'rb'),
                    'eo': open(eo_fname, 'rb')
                }
                r = requests.post(self.url + 'ldm_upload/' + self.current_project_id, files=files)
                return r
            except Exception as e:
                return e


if __name__ == '__main__':
    livedronemap = Livedronemap('http://127.0.0.1:5000/')
    res = livedronemap.create_project('test2345')
    print(res)
    livedronemap.set_current_project('test2345')

    # result = livedronemap.ldm_upload('example_upload/2018-09-28_152851.jpg', 'example_upload/2018-09-28_152851.txt')
    # print(result)
