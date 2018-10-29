import requests
import json
import nanotime


class Mago3D:
    def __init__(self, url, user_id, api_key):
        self.url = url
        self.user_id = user_id
        self.headers = None
        self.api_key = api_key

        self.set_headers()
        self.get_token()

    def set_headers(self, token='', role='ADMIN', algorithm='sha', type='jwt,mac'):
        current_time = int(nanotime.now())
        headers_content = "user_id=%s" \
                          "&api_key=%s" \
                          "&token=%s" \
                          "&role=%s" \
                          "&algorithm=%s" \
                          "&type=%s" \
                          "&timestamp=%s" % (self.user_id, self.api_key, token, role, algorithm, type, current_time)
        self.headers = {'live_drone_map': headers_content}

    def get_token(self, auto_set_headers=True):
        res = requests.post(url=self.url + 'authentication/tokens/', headers=self.headers)
        token = res.json()['token']
        if auto_set_headers:
            self.set_headers(token=token)
        return token

    def upload(self, img_fname, img_metadata):
        data = {'file_meta': json.dumps(img_metadata)}
        files = {
            'file': open(img_fname, 'rb')
        }
        res = requests.post(url=self.url + 'transfer-data/', headers=self.headers, files=files, data=data)
        return res
