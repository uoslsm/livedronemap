import requests, json



def upload(url, api_key, img_fname, eo_fname):
    files = {
        'img': open(img_fname, 'rb'),
        'eo': open(eo_fname, 'rb')
    }
    r = requests.post(url, files=files)
    return r


if __name__ == '__main__':
    r = upload('http://127.0.0.1:5000/ldm_upload/', 'asdf', '2018-06-19_171528_sony.jpg', '2018-06-19_171528_insp.txt')
    print(r.text)