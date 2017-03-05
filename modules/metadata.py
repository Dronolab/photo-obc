import pyexiv2
import struct
import datetime

pyexiv2.xmp.register_namespace('http://dronolab.com/', 'dronolab')


def to_dddmm_mmmmk(value, loc):
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    value = abs(value)
    a, b = divmod(value, 1)
    a = int(a)
    b *= 60
    b = "{:.4f}".format(b)
    return str(a) + ',' + str(b) + loc_value


def to_deg(value, loc):
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg = int(abs_value)
    t1 = (abs_value - deg) * 60
    _min = int(t1)
    sec = round((t1 - _min) * 60, 5)
    return deg, _min, sec, loc_value


def xmp_write(file_path, alt_agl, alt_msl, lat, lng, hdg, drll, dpch, dyaw,
              imgw,
              ts):

    lat_deg = to_dddmm_mmmmk(lat, ["S", "N"])
    lng_deg = to_dddmm_mmmmk(lng, ["W", "E"])

    metadata = pyexiv2.ImageMetadata(file_path)
    metadata.read()

    metadata['Xmp.dronolab.RelativeAltitude'] = str(alt_agl)
    metadata['Xmp.dronolab.AbsoluteAltitude'] = str(alt_msl)
    metadata['Xmp.dronolab.GPSLongitude'] = lng_deg
    metadata['Xmp.dronolab.GPSLatitude'] = lat_deg
    metadata['Xmp.dronolab.GPSBearing'] = str(hdg)
    metadata['Xmp.dronolab.GPSBearingRef'] = 'MAGNETIC'
    metadata['Xmp.dronolab.GimbalRollDegree'] = str(drll)
    metadata['Xmp.dronolab.GimbalPitchDegree'] = str(dpch)
    metadata['Xmp.dronolab.GimbalYawDegree'] = str(dyaw)
    metadata['Xmp.dronolab.DroneRollDegree'] = str(drll)
    metadata['Xmp.dronolab.DronePitchDegree'] = str(dpch)
    metadata['Xmp.dronolab.DroneYawDegree'] = str(dyaw)
    metadata['Xmp.dronolab.ImageWeight'] = str(imgw)

    #tmp = timestamp[:10] + '.' + timestamp[10:]
    print ts
    metadata['Xmp.dronolab.TimeStamp'] = to_xmp_format_timestamp(int(ts))

    metadata.write()


def to_xmp_format_timestamp(dt):
    return datetime.datetime.utcfromtimestamp(dt).strftime("%Y-%m-%d %H:%M:%S")


def exif_write(file_path, lat, lng, hdg, alt, drll, dpch):
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    if alt < 0:
        rel_byte = '1'
    else:
        rel_byte = '0'

    exiv_lat = (pyexiv2.Rational(lat_deg[0] * 60 + lat_deg[1], 60),
                pyexiv2.Rational(lat_deg[2] * 100, 6000),
                pyexiv2.Rational(0, 1))
    exiv_lng = (pyexiv2.Rational(lng_deg[0] * 60 + lng_deg[1], 60),
                pyexiv2.Rational(lng_deg[2] * 100, 6000),
                pyexiv2.Rational(0, 1))
    exiv_hdg = pyexiv2.Rational(hdg, 360)
    exiv_alt = pyexiv2.Rational(alt, 100000000)

    exiv_image = pyexiv2.ImageMetadata(file_path)
    exiv_image.read()
    exif_keys = exiv_image.exif_keys

    #exiv_r_b = bytarray(struct.pack("f", drll))
    #exiv_p_b = bytarray(struct.pack("f", dpch))
    #exiv_r_p = exiv_r_b.append(exiv_p_b)

    exiv_image["Exif.GPSInfo.GPSLatitude"] = exiv_lat
    exiv_image["Exif.GPSInfo.GPSLatitudeRef"] = lat_deg[3]
    exiv_image["Exif.GPSInfo.GPSLongitude"] = exiv_lng
    exiv_image["Exif.GPSInfo.GPSLongitudeRef"] = lng_deg[3]
    exiv_image["Exif.Image.GPSTag"] = 654
    exiv_image["Exif.GPSInfo.GPSMapDatum"] = "WGS-84"
    exiv_image["Exif.GPSInfo.GPSVersionID"] = '2 0 0 0'
    exiv_image["Exif.GPSInfo.GPSDestBearing"] = exiv_hdg
    exiv_image["Exif.GPSInfo.GPSDestBearingRef"] = 'M'
    exiv_image["Exif.GPSInfo.GPSAltitude"] = exiv_alt
    exiv_image["Exif.GPSInfo.GPSAltitudeRef"] = rel_byte
    #exiv_image["Exif.Photo.UserComment"] = exiv_r_p

    exiv_image.write()
