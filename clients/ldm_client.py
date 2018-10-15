import requests


class Livedronemap:
    def __init__(self, url):
        self.url = url
        self.current_project = None

    def create_project(self, project_name):
        project_json = {
            'mode': 'create',
            'name':  project_name
        }
        r = requests.post(self.url + 'project/', json=project_json)
        return r

    def read_project(self):
        r = requests.get(self.url + 'project/')
        return r.json()

    def set_current_project(self, project_name):
        existing_projects = self.read_project()
        if project_name in existing_projects:
            self.current_project = project_name
        else:
            print('Project %s does not exist' % project_name)

    def ldm_upload(self, img_fname, eo_fname):
        if self.current_project is not None:
            try:
                files = {
                    'img': open(img_fname, 'rb'),
                    'eo': open(eo_fname, 'rb')
                }
                r = requests.post(self.url + 'ldm_upload/' + self.current_project, files=files)
                return r
            except Exception as e:
                return e


if __name__ == '__main__':
    livedronemap = Livedronemap('http://127.0.0.1:5000/')
    livedronemap.create_project('test1')
    livedronemap.set_current_project('test1')
    result = livedronemap.ldm_upload('example_upload/2018-09-28_152851.jpg', 'example_upload/2018-09-28_152851.txt')
    print(result)
