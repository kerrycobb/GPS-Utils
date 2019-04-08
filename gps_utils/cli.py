import click
import gps_utils

################################################################################
# gps2csv
@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--device', default='GARMIN', help='Name of device to get waypoints from. Default: GARMIN')

def csv_cli(device):
    '''Load waypoints from GPS into csv file'''
    gps_utils.to_csv(device)


################################################################################
# gps2kml
@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--device', default='GARMIN', help='Name of device to get data from. Default: GARMIN')
@click.option('--output', default=None, type=click.File('wb'), help='Path to output file. Default: "<current workdir path>/<device name>.kml"')
@click.option('--data', default='all', help='Data to load from gps. Valid options are: "all", "tracks", "waypoints"')
@click.option('--archive', type=click.BOOL, default=True, help='Load archived tracks, Default: True')

def kml_cli(device, output, data, archive):
    '''Load data from GPS into Google Earth'''
    gps_utils.to_kml(device=device, output=output, data=data, archive=archive)
