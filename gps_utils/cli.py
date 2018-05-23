import click
import gps_utils


################################################################################
# gps2csv
@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--device', default='GARMIN', help='Name of device to get waypoints from. Default: GARMIN')
@click.option('--format', default='csv', help='File format to output waypoints to. Default: csv')
@click.option('--sort_by', default='name', help='Column to be sorted in output csv; use "name", "date", "time", "latitude", or "elev". Default: name')
@click.option('--auto_open', default=True, type=click.BOOL,  help='Open file automatically. Default: True')
@click.option('--output', default=None, type=click.File('wb'), help='Path to output file. Default: <current workdir path>/<device name>.csv')

def csv_cli(device, format, sort_by, auto_open, output):
    '''Load data from GPS into csv file and open in system default application'''
    gps = gps_utils.GPS(device=device)
    gps.to_csv(format=format, sort_by=sort_by, auto_open=auto_open, output=output)


################################################################################
# gps2kml
@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--device', default='GARMIN', help='Name of device to get waypoints from. Default: GARMIN')
@click.option('--output', default=None, type=click.File('wb'), help='Path to output file. Default: "<current workdir path>/<device name>.kml"')
@click.option('--auto_open', default=True, type=click.BOOL,  help='Open file automatically. Default: True')
@click.option('--data', default='all', help='Data to load from gps. Valid options are: "all", "tracks", "waypoints"')
@click.option('--archive', type=click.BOOL, default=True, help='Load archived tracks, Default: True')

def kml_cli(device, output, auto_open, data, archive):
    '''Load data from GPS into Google Earth'''
    gps = gps_utils.GPS(device=device)
    gps.to_kml(output=output, auto_open=auto_open, data=data, archive=archive)
