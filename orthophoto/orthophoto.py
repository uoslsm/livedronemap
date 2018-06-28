import ctypes as c


def ortho_rectify(input_file_path_tmp, output_file_path_tmp, eo_name_tmp, image_name_tmp, pixel_size, focal_length, gsd, ground_height):
    input_file_path = input_file_path_tmp.encode('utf-8')
    output_file_path = output_file_path_tmp.encode('utf-8')
    eo_name = eo_name_tmp.encode('utf-8')
    image_name = image_name_tmp.encode('utf-8')
    mydll = c.CDLL('./Project_Ortho.dll')
    myfunc = mydll['ortho']
    myfunc.argtypes = (c.c_char_p, c.c_char_p, c.c_char_p, c.c_char_p, c.c_double, c.c_double, c.c_double, c.c_double)
    myfunc(input_file_path, output_file_path, eo_name, image_name, focal_length, gsd, pixel_size, ground_height)


if __name__ == '__main__':
    ortho_rectify(input_file_path_tmp="D:\\python-workspace\\livedronemap\\orthophoto\\workspace\\",
                  output_file_path_tmp="D:\\python-workspace\\livedronemap\\orthophoto\\workspace\\result\\",
                  eo_name_tmp="2017-04-10_125832.txt",
                  image_name_tmp="2017-04-10_125832.jpg",
                  pixel_size=0.000006,
                  focal_length=0.035,
                  gsd=0.10,
                  ground_height=23)
