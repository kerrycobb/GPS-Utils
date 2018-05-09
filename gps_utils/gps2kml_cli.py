import click
import gps_utils

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--device', default='GARMIN', help='Name of device to get waypoints from. Default: GARMIN')
@click.option('--output', default=None, type=click.File('wb'), help='Path to output file. Default: "<current workdir path>/<device name>.kml"')
@click.option('--auto_open', default=True, type=click.BOOL,  help='Open file automatically. Default: True')
@click.option('--data', default='all', help='Data to load from gps. Valid options are: "all", "tracks", "waypoints"')
@click.option('--archive', default=True, help='Load archived tracks')

def cli(device, output, auto_open, data, archive):
    '''Load data from GPS into Google Earth'''
    gps_utils.gps2kml(device=device, output=output, auto_open=auto_open, data=data, archive=archive)
