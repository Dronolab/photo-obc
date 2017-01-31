
def xmp_write(file_path, altAGL, altMSL, lat, lng, hdg, drll, dpch, dyaw, imgw, ts):
	lat_deg = to_dddmm_mmmmk(lat, ["S", "N"])
	lng_deg = to_dddmm_mmmmk(lng, ["W", "E"])

	metadata = pyexiv2.ImageMetadata(file_path)
	metadata.read()
	pyexiv2.xmp.register_namespace('http://dronolab.com/', 'dronolab')

	metadata['Xmp.dronolab.RelativeAltitude'] = str(altAGL)
	metadata['Xmp.dronolab.AbsoluteAltitude'] = str(altMSL)
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
	metadata['Xmp.dronolab.TimeStamp'] = toFormatTimestamp(float(ts))

	metadata.write()

def exif_write(file_path, lat, lng, hdg, alt, drll, dpch):

	lat_deg = to_deg(lat, ["S", "N"])
	lng_deg = to_deg(lng, ["W", "E"])

	if alt < 0:
	   	rel_byte = '1'
	else:
		rel_byte = '0'

	exiv_lat = (pyexiv2.Rational(lat_deg[0]*60+lat_deg[1],60),pyexiv2.Rational(lat_deg[2]*100,6000), pyexiv2.Rational(0, 1))
	exiv_lng = (pyexiv2.Rational(lng_deg[0]*60+lng_deg[1],60),pyexiv2.Rational(lng_deg[2]*100,6000), pyexiv2.Rational(0, 1))
	exiv_hdg = pyexiv2.Rational(hdg, 360)
	exiv_alt = pyexiv2.Rational(alt, 100000000)

	exiv_image = pyexiv2.ImageMetadata(file_path)
	exiv_image.read()
	exif_keys = exiv_image.exif_keys

	exiv_r_b = bytarray(struct.pack("f", rll))
	exiv_p_b = bytarray(struct.pack("f", pch))
	exiv_r_p = exiv_r_b.append(exiv_p_b)

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
	exiv_image["Exif.Photo.UserComment"] = exiv_r_p

	exiv_image.write()
