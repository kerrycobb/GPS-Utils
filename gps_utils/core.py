import os
import sys
import glob
import psutil
from datetime import datetime, timezone
from dateutil import tz
import subprocess
import collections
import gpxpy
import folium
import pandas as pd
from timezonefinder import TimezoneFinder
import collections
import simplekml

def auto_open_path(path):
    if sys.platform.startswith("darwin"):
        subprocess.Popen(["open", path], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
    elif os.name == "nt":
        os.startfile(path)
    elif os.name == "posix":
        subprocess.Popen(["xdg-open", path], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
    else:
        print("Operating system not recognized. Unable to auto open file")

class GPS():
    def __init__(self, device="GARMIN"):
        partitions = psutil.disk_partitions()
        mount_paths = [p.mountpoint for p in partitions if device in p.mountpoint]
        if not mount_paths:
            sys.exit((
                "Error!\n"
                "No device found with name: {}\n"
                "Check that device is plugged in or that device name is correct\n"
                "A custom device name can be provided using the option: --device").format(device))
        elif len(mount_paths) > 1:
            sys.exit("Error! \n Multiple devices found with name: {}".format(device))
        self.mount_path = mount_paths[0]
        self.device_name = device
        self.waypoints = []
        self.current_track = []
        self.archived_tracks = []

    def get_waypoints(self):
        waypoints_dir_path = os.path.join(self.mount_path, "Garmin/GPX")
        waypoint_gpx_files = glob.glob(os.path.join(waypoints_dir_path, "*.gpx"))
        for file in waypoint_gpx_files:
            gpx = gpxpy.parse(open(file))
            self.waypoints.extend(gpx.waypoints)

    def get_current_tracks(self):
        current_file = os.path.join(self.mount_path, "Garmin/GPX/Current/Current.gpx")
        gpx = gpxpy.parse(open(current_file))
        self.current_track.extend(gpx.tracks)

    def get_archived_tracks(self):
        archive_path = os.path.join(self.mount_path, "Garmin/GPX/Archive")
        archive_files = glob.glob(os.path.join(archive_path, "*.gpx"))
        for file in archive_files:
            gpx = gpxpy.parse(open(file))
            self.archived_tracks.extend(gpx.tracks)

    def to_df(self):
        if not self.waypoints:
            self.get_waypoints()
        data = []
        tf = TimezoneFinder()
        for wp in self.waypoints:
            d = collections.OrderedDict()
            d["name"] = wp.name
            d["latitude"] = wp.latitude
            d["longitude"] = wp.longitude
            d["elev (m)"] = wp.elevation
            if wp.time:
                local_tz = tf.certain_timezone_at(lng=wp.longitude, lat=wp.latitude)
                local_dt = wp.time.replace(tzinfo=timezone.utc).astimezone(tz=tz.gettz(local_tz))
                d["year (local)"] = local_dt.year
                d["month (local)"] = local_dt.month
                d["day (local)"] = local_dt.day
                d["time (local)"] = str(local_dt.time().strftime("%H:%M"))
                d["timezone (local)"] = local_tz
                d["year (UTC)"] =  wp.time.year
                d["month (UTC)"] = wp.time.month
                d["day (UTC)"] = wp.time.day
                d["time (UTC)"] = str(wp.time.time().strftime("%H:%M"))
            else:
                d["year (local)"] = None
                d["month (local)"] = None
                d["day (local)"] = None
                d["time (local)"] = None
                d["timezone (local)"] = None
                d["year (UTC)"] = None
                d["month (UTC)"] = None
                d["day (UTC)"] = None
                d["time (UTC)"] = None
            data.append(d)
        df = pd.DataFrame(data)
        return df

    def make_map(self, output=None, waypoints=True, current_track=True,
            archived_track=True, auto_open=True):
        m = folium.Map(tiles="Stamen Terrain")
        folium.TileLayer("openstreetmap").add_to(m)
        # TODO: Figure out how to add this layer, currently throws error
        # folium.TileLayer("MapQuest Open Aerial").add_to(m)
        folium.LayerControl().add_to(m)
        if waypoints:
            if not self.waypoints:
                self.get_waypoints()
            for wp in self.waypoints:
                m.add_child(folium.Marker(
                    location=[wp.latitude, wp.longitude],
                    popup=folium.Popup(self.__wp_data_str(wp), max_width=200)))
        if current_track:
            if not self.current_track:
                self.get_current_tracks()
            for track in self.current_track:
                self.__add_track_to_map(track, m)
        if archived_track:
            if not self.archived_tracks:
                self.get_archived_tracks()
            for track in self.archived_tracks:
                self.__add_track_to_map(track, m)
        if output:
            map_path = output
        else:
            map_path = os.path.join(os.getcwd(),
                    "{}.html".format(self.device_name))
        m.fit_bounds(m.get_bounds())
        m.save(map_path)
        if auto_open:
            auto_open_path(map_path)

    def __wp_data_str(self, wp, name=True, date=True):
        popup = []
        if wp.name:
            if name:
                popup.append(wp.name)
        if wp.time:
            if date:
                popup.append("{year}-{month}-{day}".format(
                    year=wp.time.year,
                    month=wp.time.month,
                    day=wp.time.day))
        if popup:
            pop_str = "<br>".join(popup)
        else:
            pop_str = "None"
        return pop_str

    def __add_track_to_map(self, track, m):
        for segment in track.segments:
            points = []
            for point in segment.points:
                points.append((point.latitude, point.longitude))
            folium.PolyLine(points).add_to(m)

    def make_kml(self, output=None, waypoints=True, current_track=True,
            archived_track=True, auto_open=True):
        kml = simplekml.Kml()
        if waypoints:
            if not self.waypoints:
                self.get_waypoints()
            for wp in self.waypoints:
                kml.newpoint(
                    name=wp.name,
                    coords=[(wp.longitude, wp.latitude, wp.elevation)],
                    description=self.__wp_data_str(wp, name=False))
        if current_track:
            if not self.current_track:
                self.get_current_tracks()
            for track in self.current_track:
                self.__add_track_to_kml(track, kml)
        if archived_track:
            if not self.archived_tracks:
                self.get_archived_tracks()
            for track in self.archived_tracks:
                self.__add_track_to_kml(track, kml)
        if output:
            kml_path = output
        else:
            kml_path = os.path.join(os.getcwd(),
                    "{}.kml".format(self.device_name))
        kml.save(kml_path)
        if auto_open:
            auto_open_path(kml_path)

    def __add_track_to_kml(self, track, kml):
        for segment in track.segments:
            coords = []
            for point in segment.points:
                coords.append(tuple([point.longitude, point.latitude, point.elevation]))
            ls = kml.newlinestring(name=None, coords=coords)
            ls.style.linestyle.width = 2
            ls.style.linestyle.color = simplekml.Color.blue

