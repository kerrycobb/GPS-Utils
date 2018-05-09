import os
import sys
import glob
import psutil
import gpxpy
import pandas
import subprocess

def gps2csv(device='GARMIN', format='csv', sort_by='name', auto_open=True, output=None):

    partitions = psutil.disk_partitions()
    mount_paths = [p.mountpoint for p in partitions if device in p.mountpoint]

    if not mount_paths:
        sys.exit('Error! \n No device found with name: {} \n Check that device is plugged in or that device name is correct \n A custom device name can be provided using the option: --device'.format(device))
    elif len(mount_paths) > 1:
        sys.exit('Error! \n Multiple devices found with name: {}'.format(device))

    garmin_mount_path = mount_paths[0]
    waypoints_path = os.path.join(garmin_mount_path, 'Garmin/GPX')
    gpx_files = glob.glob(os.path.join(waypoints_path, '*.gpx'))
    waypoints = []
    for f in gpx_files:
        gpx_file = open(f)
        gpx = gpxpy.parse(gpx_file)
        for wp in gpx.waypoints:
            name = wp.name
            date = wp.time.date().isoformat()
            time = wp.time.time().isoformat()
            lat = wp.latitude
            lon = wp.longitude
            elev = wp.elevation
            waypoint = [name, date, time, lat, lon, elev]
            waypoints.append(waypoint)

    headers = ['name', 'date', 'time', 'latitude', 'longitude', 'elev']
    df = pandas.DataFrame(waypoints, columns=headers).sort_values(sort_by)

    if output:
        outpath = os.path.abspath(output)
    else:
        outpath = os.path.join(os.getcwd(), '{}'.format(device))

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
        if os.name == 'nt':
            os.startfile(path)
        else:
            subprocess.call(('open', path))

    print('{} file saved to {}'.format(format, os.path.abspath(path)))
