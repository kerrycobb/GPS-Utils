import setuptools as st

st.setup(
    name="GPS-Utils",
    version="1.0",
    description="GPS utilities",
    url="http://github.com/kerrycobb/gps-utils",
    author="Kerry A. Cobb",
    author_email="cobbkerry@gmail.com",
    license="GPLv3",
    packages=st.find_packages(),
    install_requires=[
        "gpxpy",
        "pandas",
        "click",
        "simplekml",
        "psutil",
        "timezonefinder"],
    entry_points={
        "console_scripts":[
            "gps2kml=gps_utils.cli:kml_cli",
            "gps2csv=gps_utils.cli:csv_cli",
            "gps2map=gps_utils.cli:map_cli"]
    },
)
