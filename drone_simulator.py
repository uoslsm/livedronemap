import requests, json

mydata = {
    'api_key': 'university-of-seoul-sangwoo-ham-1234567890',
    'fname_image': 'example.jpg',
    'fname_eo': 'example.txt',
    'f_image': 'example_image_file_object',
    'f_eo': 'example_eo_file_object',
    'x_w': 127.2303,
    'y_w': 38.0002,
    'z_w': 30.22,
    'omega': 0.002,
    'phi': 0.0004,
    'kappa': 232
}

mydata = json.dumps(mydata) #Encode JSON: Dictionary -> JSON
r = requests.post('http://127.0.0.1:5000/ldm_upload_data', json=mydata)

print('Done')