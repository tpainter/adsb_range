# adsb_range
*Compare the range of ADS-B receivers.*

# Description
adsb_range is a short python program that connects to an ADSB receiver that produces output in basestation (csv) format. As it gathers aircraft positions, it keeps track of the farthest points away from the receiver.

It periodically writes the coordinates of these points to a *.kml file for easy viewing in maping programs.

# Requirements
Requires the installation of Twisted. 'pip install twisted'

# Usage

'python adsb_range.py -a [ip address of adsb receiver] --lat [latitude of antenna in decimal] --lon [longitude of antenna in decimal]'

Example:
'python adsb_range.py -a 192.168.0.100 --lat 45.678 --lon -87.654'

# References
Uses py1090 message library from https://github.com/jojonas/py1090

# License
Apache 2.0 - see LICENSE.txt
