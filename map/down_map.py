import math
import os
import logging
import logging.handlers
import datetime
from urllib import request
from PIL import Image
import configparser
import time
import urllib.request


class MapDownloader(object):
    def __init__(self, lat_start, lng_start, lat_end, lng_end, zoom=12, site='https://mt2.google.cn/vt/lyrs=s&x=',tile_size=256, root_path='.\\'):
        self.lat_start = lat_start
        self.lng_start = lng_start
        self.lat_end = lat_end
        self.lng_end = lng_end
        self.zoom = zoom
        self.tile_size = tile_size
        self.root_path = os.path.dirname(os.path.realpath(__file__))
        self.site = site

        self._generate_xy_point()

    def _generate_xy_point(self):
        self._x_start, self._y_start = self._convert_latlon_to_xy(self.lat_start, self.lng_start)
        print('x1=%d,y1=%d' %(self._x_start, self._y_start))
        self._x_end, self._y_end = self._convert_latlon_to_xy(self.lat_end, self.lng_end)
        print('x2=%d,y2=%d' %(self._x_end, self._y_end))

    def _convert_latlon_to_xy(self, lat, lng):
        tiles_count = 1 << self.zoom

        point_x = (self.tile_size / 2 + lng * self.tile_size / 360.0) * tiles_count // self.tile_size
        sin_y = math.sin(lat * (math.pi / 180.0))
        point_y = ((self.tile_size / 2) + 0.5 * math.log((1 + sin_y) / (1 - sin_y)) *
                   -(self.tile_size / (2 * math.pi))) * tiles_count // self.tile_size

        return int(point_x), int(point_y)

    def generate_image(self, filename):
        width, height = 256 * (self._x_end + 1 - self._x_start), 256 * (self._y_end + 1 - self._y_start)
        map_img = Image.new('RGB', (width, height))
		
        os.mkdir('.\\'+str(self.zoom))
        os.chdir('.\\'+str(self.zoom))

        p_curr, p_target = 1, (self._x_end + 1 - self._x_start) * (self._y_end + 1 - self._y_start)

        for x in range(0, self._x_end + 1 - self._x_start):
            current_dir = str(self._x_start + x)
            os.mkdir(current_dir)
            os.chdir(current_dir)
            for y in range(0, self._y_end + 1 - self._y_start):
                print('Processing tile #{} of {}'.format(p_curr, p_target))

                url = self.site + str(self._x_start + x) + '&y=' + str(self._y_start + y) + '&z=' + str(self.zoom)
				
                print(url)

                current_tile = 'g' + str(self._x_start + x) + '_' + str(self._y_start + y) + '_' + str(self.zoom) + '.jpg'
                #request.urlretrieve(url, current_tile)
                #request.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.168 Safari/537.36")
                opener=urllib.request.build_opener()
                opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(url, current_tile)

                # im = Image.open(current_tile)
                # map_img.paste(im, (x * 256, y * 256))
                # map_img.save(filename)

                # os.remove(current_tile)

                p_curr += 1

            os.chdir(os.path.dirname('..\\'))
            time.sleep(1)
        os.chdir(self.root_path)

def main():
    pro_path=os.path.dirname(os.path.realpath(__file__))
    config_path=os.path.join(pro_path,'Parameter.ini')
    conf=configparser.ConfigParser()
    conf.read(config_path)
    lat_start = float(conf.get('coordinate', 'lat_start'))
    lng_start = float(conf.get('coordinate', 'lng_start'))
    lat_end = float(conf.get('coordinate', 'lat_end'))
    lng_end = float(conf.get('coordinate', 'lng_end'))
    zoom_min = int(conf.get('level', 'zoom_min'))
    zoom_max = int(conf.get('level', 'zoom_max'))
    site = conf.get('website', 'site')
    print("%d" %(zoom_min))
    print("%d" %(zoom_max))
    print("%s" %(lat_start))
    print("%s" %(lng_start))
    print("%s" %(lat_end))
    print("%s" %(lng_end))
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

    logging.basicConfig(filename='my.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

    logging.error("Log start.")
    for a in range(zoom_min, zoom_max):
        try:
            md = MapDownloader(lat_start, lng_start, lat_end, lng_end, a, site)
            md.generate_image('2.jpg')
            print("The map has successfully been created")
        except Exception as e:
            print("Could not generate the image - try adjusting the zoom level and checking your coordinates. Cause: {}".format(e))
            logging.error("Could not generate the image. Cause: {}".format(e))
            os.chdir(pro_path)


if __name__ == '__main__':
    main()