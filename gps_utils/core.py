import os
import sys
import glob
import psutil
import gpxpy
import pandas as pd
from timezonefinder import TimezoneFinder
from datetime import datetime, timezone
from dateutil import tz
import collections
import simplekml

def to_csv(device):
    partitions = psutil.disk_partitions()
    mount_path = [p.mountpoint for p in partitions if device in p.mountpoint][0]
    waypoints_path = os.path.join(mount_path, 'Garmin/GPX')
    waypoint_files = glob.glob(os.path.join(waypoints_path, '*.gpx'))
    data = []
    for f in waypoint_files:
        gpx_file = open(f)
        gpx = gpxpy.parse(gpx_file)
        tf = TimezoneFinder()
        for wp in gpx.waypoints:
            local_tz = tf.certain_timezone_at(lng=wp.longitude, lat=wp.latitude)
            local_dt = wp.time.replace(tzinfo=timezone.utc).astimezone(tz=tz.gettz(local_tz))
            data.append(collections.OrderedDict({
                'name': wp.name,
                'latitude': wp.latitude,
                'longitude': wp.longitude,
                'elev (m)': wp.elevation,
                'year (local)': local_dt.year,
                'month (local)': local_dt.month,
                'day (local)': local_dt.day,
                'time (local)': str(local_dt.time().strftime('%H:%M')),
                'timezone (local)': local_tz,
                'year (UTC)': wp.time.year,
                'month (UTC)': wp.time.month,
                'day (UTC)': wp.time.day,
                'time (UTC)': str(wp.time.time().strftime('%H:%M')),
            }))
    df = pd.DataFrame(data)
    df.to_csv('GARMIN.csv', index=False)

def to_kml(device='GARMIN', output='GARMIN.kml', data='all', archive=True):
    partitions = psutil.disk_partitions()
    mount_path = [p.mountpoint for p in partitions if device in p.mountpoint][0]
    kml = simplekml.Kml()
    if data == 'all' or data == 'waypoints':
        waypoints_path = os.path.join(mount_path, 'Garmin/GPX')
        waypoint_files = glob.glob(os.path.join(waypoints_path, '*.gpx'))
        for f in waypoint_files:
            gpx_file = open(f)
            gpx = gpxpy.parse(gpx_file)
            for wp in gpx.waypoints:
                coords = [tuple([wp.longitude, wp.latitude, wp.elevation])]
                description = 'Date: {} <br> Time: {}'.format(wp.time.date, wp.time.time())
                kml.newpoint(name=wp.name, coords=coords, description=description)
    if data == 'all' or data == ' tracks':
        current_file = os.path.join(mount_path, 'Garmin/GPX/Current/Current.gpx')
        if archive:
            archive_path = os.path.join(mount_path, 'Garmin/GPX/Archive')
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
    if output:
        kml_path = output
    else:
        kml_path = '{}.kml'.format(device)
    kml.save(kml_path)
