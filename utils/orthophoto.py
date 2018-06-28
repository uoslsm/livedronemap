import ctypes as c
import os

def rectify(input_dir, output_dir, eo_fname, img_fname, pixel_size, focal_length, gsd, ground_height):
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


if __name__ == '__main__':
    rectify(input_dir="D:\\python-workspace\\livedronemap\\utils\\workspace\\",
            output_dir="D:\\python-workspace\\livedronemap\\utils\\workspace\\result\\",
            eo_fname="2017-04-10_125832.txt",
            img_fname="2017-04-10_125832.jpg",
            pixel_size=0.000006,
            focal_length=0.035,
            gsd=0.10,
            ground_height=23)

