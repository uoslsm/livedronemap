import exifread

# TODO: DJI 사진에서 좌표 빼오기

def read_eo(fname):
    def dms2dec(dms):
        d = dms.values[0].num / dms.values[0].den
        m = dms.values[1].num / dms.values[1].den
        s = dms.values[2].num / dms.values[2].den
        return d + m / 60 + s / 60 / 60

    f = open(fname,'rb')
    tags = exifread.process_file(f)

    lon = dms2dec(tags['GPS GPSLongitude'])
    lat = dms2dec(tags['GPS GPSLatitude'])

    return lon, lat


if __name__ == '__main___':
    lon, lat = read_eo('DJI_0100.JPG')
    print(lon)
    print(lat)