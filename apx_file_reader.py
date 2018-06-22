from system_calibration import calibrate


# file read
def read_eo_file(fname):
    f = open(fname, 'r')
    data = f.readlines()

    # parsing data from input file
    def parse_sensor_data(data):
        temp_list = data.split(',')
        parsing_list_temp = [temp_list[1], temp_list[3], temp_list[5], temp_list[7], temp_list[8], temp_list[9]]
        parsing_list = [float(i) for i in parsing_list_temp]
        return parsing_list

    data1 = parse_sensor_data(data[0])
    data2 = parse_sensor_data(data[2])

    lat = (data1[0] + data2[0]) / 2 / 100
    lon = (data1[1] + data2[1]) / 2 / 100
    alt = (data1[2] + data2[2]) / 2
    roll = (data1[3] + data2[3]) / 2
    pitch = (data1[4] + data2[4]) / 2
    yaw = (data1[5] + data2[5]) / 2

    OPK = calibrate(roll, pitch, yaw)
    omega = OPK[0]
    phi = OPK[1]
    kappa = OPK[2]
    # omega, phi, kappa == radian
    calibrated_eo = {
        'lat': lat,
        'lon': lon,
        'alt': alt,
        'omega': omega,
        'phi': phi,
        'kappa': kappa
    }
    f.close()
    return calibrated_eo


if __name__ == '__main__':
    calibrated_eo = read_eo_file('2018-06-19_172040_insp.txt')
    print(calibrated_eo)