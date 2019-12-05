import os
import click
from .core import GPS

# gps2csv
@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("--device", default="GARMIN", 
        help="Name of device to get waypoints from. Default: GARMIN")
@click.option("--output", default=None, type=click.File("wb"), 
        help="Path to output file. Default: <current workdir path>/<device name>.csv")
def csv_cli(device, output):
    """Load waypoints from GPS into csv file"""
    gps = GPS(device=device)
    df = gps.to_df()
    if output:
        csv_path = output
    else:
        csv_path = os.path.join(os.getcwd(), "{}.csv".format(gps.device_name))
    df.to_csv(csv_path, index=False)

#gps2map
@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("--device", default="GARMIN", 
        help="Name of device to get data from. Default: GARMIN")
@click.option("--output", default=None, type=click.File("wb"), 
        help="Path to output file. Default: <current workdir path>/<device name>.html")
def map_cli(device, output):
    """Load data from GPS into Leaflet map"""
    gps = GPS(device=device)
    gps.make_map(output=output, waypoints=True, current_track=True, 
            archived_track=True, auto_open=True)

# gps2kml
@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("--device", default="GARMIN", 
        help="Name of device to get data from. Default: GARMIN")
@click.option("--output", default=None, type=click.File("wb"), 
        help="Path to output file. Default: <current workdir path>/<device name>.kml")
def kml_cli(device, output):
    """Load data from GPS into Google Earth"""
    gps = GPS(device=device)
    gps.make_kml(output=output, waypoints=True, current_track=True, 
            archived_track=True, auto_open=True)