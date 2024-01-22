from pyembedded.gps_module.gps import GPS
# from pickle import loads
import time
gps = GPS(port = 'COM16',baud_rate=9600)
while True:
    lat,long=gps.get_lat_long()
    no_of_sat = gps.get_no_of_satellites()
    print('latitude : {} longitude : {} Satellite Count : {}'.format(lat,long,no_of_sat))
    time.sleep(1)

