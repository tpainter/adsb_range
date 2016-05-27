# adsb_range
*Display the range of ADS-B receivers in a kml file.*

## Description
adsb_range is a short python program that connects to an ADSB receiver that produces output in basestation (csv) format. As it gathers aircraft positions, it keeps track of the farthest points away from the receiver.

It periodically (every 5 minutes) writes the coordinates of these points to a *.kml file for easy viewing in maping programs. Collection will stop after 24 hours.

## Requirements
No specific packages are required, but if Twisted is installed, it will be used.

## Usage
Basic usage is to specify the address of an ADSB receiver that is providing basestation data on the default port. The location of the receiver will be 'guessed' based on the messages being received.

`python adsb_range.py -a [ip address of adsb receiver]`

The receiver's location can also be given.

`python adsb_range.py -a [ip address of adsb receiver] --lat [latitude of antenna in decimal] --lon [longitude of antenna in decimal]`

Example:
`python adsb_range.py -a 192.168.0.100 --lat 45.678 --lon -87.654`

or:
`python adsb_range.py -a 192.168.0.100 -p 30003 --lat 45.678 --lon -87.654 -n filteradded`

## References
Uses py1090 message library from https://github.com/jojonas/py1090

## License
Apache 2.0 - see LICENSE.txt
