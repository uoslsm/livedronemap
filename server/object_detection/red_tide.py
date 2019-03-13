import os
import csv
import json
import arrow
import sys


def detect_red_tide(json_template_fname, input_img_path):
    output_img_path = input_img_path.split('.')[0] + '_red_tide.tif'
    output_shp_path = input_img_path.split('.')[0] + '_red_tide.shp'
    output_wkt_path = input_img_path.split('.')[0] + '_red_tide.wkt'

    # Detect red tide area using gdal_calc
    gdal_string = """gdal_calc.bat --calc="logical_and(logical_and(logical_and(A > 81.75, A < 101.75), logical_and(B > 105.37, B < 125.37)), logical_and(C > 109, C < 129))" --format=GTiff --type=Float32 -A %s --A_band=1 -B %s --B_band=2 -C %s --C_band=3 --outfile=%s""" % (input_img_path, input_img_path, input_img_path, output_img_path)
    os.system(gdal_string)

    # Polygonize the result
    gdal_string = """gdal_polygonize.bat %s %s""" % (output_img_path, output_shp_path)
    os.system(gdal_string)

    # Convert the result from shapefile to WKT
    gdal_string = """ogr2ogr -f CSV -where "DN=1" %s %s -lco GEOMETRY=AS_WKT""" % (output_wkt_path, output_shp_path)
    os.system(gdal_string)

    detected_objects_list = []
    number = -1

    csv.field_size_limit(100000000)

    with open(os.path.join(output_wkt_path, os.path.basename(output_wkt_path).split('.')[0] + '.csv'), 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if number != -1:
                bounding_box_geometry = row[0]
                detected_objects = json.load(open(json_template_fname, 'r'))
                detected_objects['number'] = number
                detected_objects['object_type'] = '1'  # 0: 선박탐지, 1: 기름유출
                detected_objects['bounding_box_geometry'] = bounding_box_geometry
                detected_objects['detected_date'] = arrow.utcnow().format('YYYYMMDDHHmmss')
                detected_objects['insert_date'] = arrow.utcnow().format('YYYYMMDDHHmmss')
                detected_objects_list.append(detected_objects)
            number += 1

    return detected_objects_list


if __name__ == '__main__':
    res = detect_red_tide('json_template/ldm_mago3d_detected_objects.json', 'project/test_dji_red-tide/rectified/DJI_0030.tif')
    print(res[0])
