import os
import sys
import glob
import psutil
import gpxpy
import subprocess
import simplekml


def gps2kml(device='GARMIN', output=None, auto_open=True, data='all', archive=True):

    partitions = psutil.disk_partitions()
    mount_paths = [p.mountpoint for p in partitions if device in p.mountpoint]

    if not mount_paths:
        sys.exit('Error! \n No device found with name: {} \n Check that device is plugged in or that device name is correct \n A custom device name can be provided using the option: --device'.format(device))
    elif len(mount_paths) > 1:
        sys.exit('Error! \n Multiple devices found with name: {}'.format(device))

    mount_path = mount_paths[0]
    kml = simplekml.Kml()

    if data == 'all':
        tracks(mount_path, kml, archive)
        waypoints(mount_path, kml)
    elif data == 'tracks':
        tracks(mount_path, kml, archive)
    elif data == 'waypoints':
        waypoints(mount_path, kml)
    else:
        sys.exit('{} not a valid argument for "data"'.format(data))

    if output:
        kml_path = os.path.abspath(output)
    else:
        kml_path = os.path.join(os.getcwd(), '{}.kml'.format(device))

    kml.save(kml_path)

    if auto_open is True:
        if os.name == 'nt':
            os.startfile(kml_path)
        else:
            subprocess.call(('open', kml_path))

    print('KML file saved to {}'.format(kml_path))


def tracks(mount_path, kml, archive):
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
                # try:
                #     midpoint = coords[int(len(ls) / 2)]
                # except:
                #     pass 



def waypoints(mount_path, kml):
    waypoints_path = os.path.join(mount_path, 'Garmin/GPX')
    waypoint_files = glob.glob(os.path.join(waypoints_path, '*.gpx'))
    waypoints = []
    for f in waypoint_files:
        gpx_file = open(f)
        gpx = gpxpy.parse(gpx_file)
        waypoints = []
        for waypoint in gpx.waypoints:
            name = waypoint.name
            coords = [(waypoint.longitude, waypoint.latitude, waypoint.elevation)]
            date = waypoint.time.date().isoformat()
            time = waypoint.time.time().isoformat()
            description = 'Date: {}<br>Time: {}'.format(date, time)
            pnt = kml.newpoint(name=name, coords=coords, description=description)
