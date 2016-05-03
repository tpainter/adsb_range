# Copyright 2016 Travis Painter (travis.painter@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse

from twisted.internet import reactor
from adsbconnection import AdsbConnection

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog = "ADSBrange", 
        description = "Save a map shape showing the range of ADSB messages received.")
    parser.add_argument('-n', '--name', help="Name of the receiver.", default='ADSB')
    parser.add_argument('-a', '--address', help="IP address of the receiver.", required=True)
    parser.add_argument('-p', '--port', help="Basestation port of the receiver. Default 30003", default=30003)
    parser.add_argument('--lat', help="Latitude of the receiver's location in decimal. Example: 40.123", type=float, required=True)
    parser.add_argument('--lon', help="Longitude of the receiver's location in decimal. Example: -90.123", type=float, required=True)
    parser.add_argument('-j', '--json', help="Output range in JSON format instead of kml.", action='store_true')
    args = parser.parse_args()
    
    if args.json:
        format = 'json'
    else:
        format= 'kml'
        
    connections = []
    connections.append([args.name, args.address, args.port, (args.lat, args.lon), format])
    
    connectionlist = []
    
    for c in connections:
        h = AdsbConnection(c[0], c[1], c[2], c[3], c[4])
        connectionlist.append(h)        
    
    reactor.run()