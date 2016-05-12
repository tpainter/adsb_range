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

import time
import sys
import json, time

from twisted.internet import reactor, threads, task
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.protocols import basic

import py1090 #This has been modified slightly to remove 'enum'
import antennarange


class AdsbConnection():
    """
    Connection to ADSB basestation receiver.
    """
    
    def __init__(self, name, address, port, center, format):
        self.name = name
        self.address = address
        self.port = port
        self.center = center     
        self.format = format    

        self.layers = 5
        self.range = antennarange.AntennaRange(self.center, 720, self.layers)
        
        if self.format == 'json':
            self.lc = task.LoopingCall(self.writeJson)
        else:
            self.lc = task.LoopingCall(self.writeKml)
        self.lc.start(5*60, now=False)
        
        # Stop after 24 hours of collecting data.
        reactor.callLater(24*60*60, self.close_connection)
        
        # Connect to ADSB receiver.
        point = TCP4ClientEndpoint(reactor, self.address, self.port)
        d = connectProtocol(point, basic.LineOnlyReceiver())
        d.addCallback(self.register_message_handler)
        
    def register_message_handler(self, connection):
        """
        Injects function that handles received messages into the connection (i.e. the protocol).
        This is used as a callback on the defered that makes the connection.
        """
        print("Connected to antenna: {}".format(self.name))
        self.connection = connection
        self.connection.lineReceived = self.message
        
    def message(self, message):
        a = py1090.Message.from_string(message)
        #sys.stdout.write(message + '\n')
        
        if a.latitude is not None:
            #print("{}: {}, {}, {}").format(a.hexident, a.latitude, a.longitude, a.altitude)
            self.range.add_point((a.latitude, a.longitude, a.altitude))
        
    def writeJson(self):
        d = threads.deferToThread(self._writeJson)
    
    def _writeJson(self):
        filename = '{}_range.json'.format(self.name)
        print("Writing points to json file: {}".format(filename))
        with open(filename, 'w') as outfile:
            json.dump(self.range.range_shape(0), outfile)
            
    def writeKml(self):
        d = threads.deferToThread(self._writeKml)
        
    def _writeKml(self):
        filename = '{}_range.kml'.format(self.name)
        print("Writing points to KML file: {}".format(filename))
        with open(filename, 'w') as outfile:
            outfile.write('''<?xml version="1.0" encoding="UTF-8"?>
                            <kml xmlns="http://www.opengis.net/kml/2.2">
                            <Folder><name>{} Ranges</name>'''.format(self.name))
            for n in range(self.layers+1):
                outfile.write('''<Placemark>
                                <name>{}_{}ft</name>
                                <Polygon>
                                  <extrude>1</extrude>
                                  <tessellate>1</tessellate>
                                  <altitudeMode>relativeToGround</altitudeMode>
                                  <outerBoundaryIs>
                                    <LinearRing>
                                      <coordinates>'''.format(self.name, n*10000))
                for i in self.range.range_shape(n):
                    # KML takes points in the form of [long],[lat],[alt]
                    if i[0] is not None:
                        outfile.write("{},{},{:.1f} ".format(i[1], i[0], n*10000/0.3048))        
                outfile.write('''
                                      </coordinates>
                                    </LinearRing>
                                  </outerBoundaryIs>
                                </Polygon>
                                </Placemark>''')
            outfile.write('''</Folder></kml>''')
                            
    def close_connection(self):
        """ Close the connection to the ADSB receiver and cleanup.
        """
        print("Stopping the program.")
        self._writeKml()
        reactor.stop()
        
        
        