import ctypes as c
import os
import cv2


def rectify(input_dir, output_dir, eo_fname, img_fname, pixel_size, focal_length, gsd, ground_height, visualize=False, visualize_time=3000):
    input_file_path = input_dir.encode('utf-8')
    output_file_path = output_dir.encode('utf-8')
    eo_name = eo_fname.encode('utf-8')
    image_name = img_fname.encode('utf-8')
    util_dir = os.path.dirname(os.path.abspath(__file__))
    dll_abs_path = os.path.join(util_dir, 'Project_Ortho.dll')
    mydll = c.CDLL(dll_abs_path)
    myfunc = mydll['ortho']
    myfunc.argtypes = (c.c_char_p, c.c_char_p, c.c_char_p, c.c_char_p, c.c_double, c.c_double, c.c_double, c.c_double)
    myfunc(input_file_path, output_file_path, eo_name, image_name, focal_length, gsd, pixel_size, ground_height)

    if visualize:
        im = cv2.imread(os.path.join(output_dir, img_fname.split('.')[0] + '.png'))
        im = cv2.resize(im, (600, 800))
        cv2.imshow('Rectified Image', im)
        cv2.waitKey(visualize_time)
        cv2.destroyAllWindows()

def rectify_UCON(input_dir, output_dir, eo_fname, img_fname, pixel_size, focal_length, gsd, ground_height, visualize=False, visualize_time=3000):
    input_file_path = input_dir.encode('utf-8')
    output_file_path = output_dir.encode('utf-8')
    eo_name = eo_fname.encode('utf-8')
    image_name = img_fname.encode('utf-8')
    util_dir = os.path.dirname(os.path.abspath(__file__))
    dll_abs_path = os.path.join(util_dir, 'Project_Ortho_UCON.dll')
    mydll = c.CDLL(dll_abs_path)
    myfunc = mydll['ortho']
    myfunc.argtypes = (c.c_char_p, c.c_char_p, c.c_char_p, c.c_char_p, c.c_double, c.c_double, c.c_double, c.c_double)
    myfunc(input_file_path, output_file_path, eo_name, image_name, focal_length, gsd, pixel_size, ground_height)

    if visualize:
        im = cv2.imread(os.path.join(output_dir, img_fname.split('.')[0] + '.png'))
        im = cv2.resize(im, (600, 800))
        cv2.imshow('Rectified Image', im)
        cv2.waitKey(visualize_time)
        cv2.destroyAllWindows()