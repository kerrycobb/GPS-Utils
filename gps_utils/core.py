import os
import sys
import glob
import psutil
import gpxpy
import pandas
import subprocess
import simplekml
from timezonefinder import TimezoneFinder
from datetime import datetime
from dateutil import tz

def utc_to_timezone(utc_date, utc_time, zone):
    d = list(map(int, utc_date.split('-')))
    t = list(map(int, utc_time.split(':')))
    utc_dt = datetime(d[0], d[1], d[2], t[0], t[1], t[2])
    utc_zone = tz.gettz('UTC')
    to_zone = tz.gettz(zone)
    utc_dt = utc_dt.replace(tzinfo=utc_zone)
    local_dt = utc_dt.astimezone(to_zone)
    return(local_dt.date().isoformat(), local_dt.time().isoformat())

class GPS():
    def __init__(self, device='GARMIN'):
        partitions = psutil.disk_partitions()
        mount_paths = [p.mountpoint for p in partitions if device in p.mountpoint]
        if not mount_paths:
            sys.exit('Error! \n No device found with name: {} \n Check that device is plugged in or that device name is correct \n A custom device name can be provided using the option: --device'.format(device))
        elif len(mount_paths) > 1:
            sys.exit('Error! \n Multiple devices found with name: {}'.format(device))
        self.mount_path = mount_paths[0]
        self.device_name = device

    def to_csv(self, format='csv', sort_by='name', auto_open=True, output=None):
        waypoints = self.get_waypoints()
        headers = ['name', 'date (UTC)', 'time (UTC)', 'lat', 'lon', 'elev (m)']
        df = pandas.DataFrame(waypoints, columns=headers).sort_values(sort_by)
        tf = TimezoneFinder()
        for i, row in df.iterrows():
            tz = tf.certain_timezone_at(lng=row['lon'], lat=row['lat'])
            df.loc[i,'timezone'] = tz
            utc_date = row['date (UTC)']
            utc_time = row['time (UTC)']
            local_datetime = utc_to_timezone(utc_date, utc_time, tz)
            df.loc[i, 'date (local)'] = local_datetime[0]
            df.loc[i, 'time (local)'] = local_datetime[1]
        df = df[['name', 'date (local)', 'time (local)', 'timezone', 'date (UTC)', 'time (UTC)', 'lat', 'lon', 'elev (m)']]
        if output:
            outpath = os.path.abspath(output)
        else:
            outpath = os.path.join(os.getcwd(), '{}'.format(self.device_name))
        if format == 'csv':
            path = '{}.csv'.format(outpath)
            df.to_csv(path, index=False)
        elif format == 'xlsx':
            path = '{}.xlsx'.format(outpath)
            writer = pandas.ExcelWriter(path)
            df.to_excel(writer,'Sheet1', index=False)
            writer.save()
        else:
            sys.exit('"{}" is not a valid file type; use csv or xlsx'.format(format))
        if auto_open is True:
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', path))
            elif os.name == 'nt': # For Windows
                os.startfile(path)
            elif os.name == 'posix': # For Linux, Mac, etc.
                subprocess.call(('xdg-open', path))
            else:
                print("Operating system not recognized. Unable to auto open KML")
        print('{} file saved to {}'.format(format, os.path.abspath(path)))

    def to_kml(self, output=None, auto_open=True, data='all', archive=True):
        kml = simplekml.Kml()
        if data == 'all':
            self.__tracks_to_simplekml(kml, archive=archive)
            self.__waypoints_to_simplekml(kml)
        elif data == 'tracks':
            self.__tracks_to_simplekml(kml, archive=archive)
        elif data == 'waypoints':
            self.__waypoints_to_simplekml(kml)
        else:
            sys.exit('{} not a valid argument for "data"'.format(data))
        if output:
            kml_path = os.path.abspath(output)
        else:
            kml_path = os.path.join(os.getcwd(), '{}.kml'.format(self.device_name))
        kml.save(kml_path)
        if auto_open is True:
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', kml_path))
            elif os.name == 'nt': # For Windows
                os.startfile(kml_path)
            elif os.name == 'posix': # For Linux, Mac, etc.
                subprocess.call(('xdg-open', kml_path))
            else:
                print("Operating system not recognized. Unable to auto open KML")
        print('KML file saved to {}'.format(kml_path))

    def get_waypoints(self):
        waypoints_dir_path = os.path.join(self.mount_path, 'Garmin/GPX')
        waypoint_gpx_files = glob.glob(os.path.join(waypoints_dir_path, '*.gpx'))
        waypoints = []
        for f in waypoint_gpx_files:
            gpx_file = open(f)
            gpx = gpxpy.parse(gpx_file)
            for wp in gpx.waypoints:
                waypoints.append([
                    wp.name,
                    wp.time.date().isoformat(),
                    wp.time.time().isoformat(),
                    wp.latitude,
                    wp.longitude,
                    wp.elevation
                ])
        return(waypoints)

    def __waypoints_to_simplekml(self, kml):
        waypoints = self.get_waypoints()
        for w in waypoints:
            coords = [tuple([w[4], w[3], w[5]])]
            description = 'Date: {}<br>Time: {}'.format(w[1], w[2])
            pnt = kml.newpoint(name=w[0], coords=coords, description=description)

    def __tracks_to_simplekml(self, kml, archive=True):
        # TODO Make current track different color
        current_file = os.path.join(self.mount_path, 'Garmin/GPX/Current/Current.gpx')
        if archive:
            archive_path = os.path.join(self.mount_path, 'Garmin/GPX/Archive')
            archive_files = glob.glob(os.path.join(archive_path, '*.gpx'))
            files = [current_file] + archive_files
        else:
            files = [current_file]
        for f in files:
            gpx_file = open(f)
            gpx = gpxpy.parse(gpx_file)
            for track in gpx.tracks:
                track_name = track.name
                for i, segment in enumerate(track.segments):
                    segment_name = '{} {}'.format(track_name, i)
                    coords = []
                    for point in segment.points:
                        point = coords.append((point.longitude, point.latitude, point.elevation))
                    ls = kml.newlinestring(name=segment_name, coords=coords)
                    ls.style.linestyle.width = 2
                    ls.style.linestyle.color = simplekml.Color.blue
