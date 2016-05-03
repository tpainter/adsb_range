
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
        
        self.range = antennarange.AntennaRange(self.center, 720)
        
        if self.format == 'json':
            self.lc = task.LoopingCall(self.writeJson)
        else:
            self.lc = task.LoopingCall(self.writeKml)
        self.lc.start(5*60, now = False)
        
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
            json.dump(self.range.range_shape(), outfile)
            
    def writeKml(self):
        d = threads.deferToThread(self._writeKml)
        
    def _writeKml(self):
        filename = '{}_range.kml'.format(self.name)
        print("Writing points to KML file: {}".format(filename))
        #print self.range.range_shape()
        with open(filename, 'w') as outfile:
            outfile.write('''<?xml version="1.0" encoding="UTF-8"?>
                            <kml xmlns="http://www.opengis.net/kml/2.2">
                              <Placemark>
                                <name>{}</name>
                                <Polygon>
                                  <extrude>1</extrude>
                                  <altitudeMode>relativeToGround</altitudeMode>
                                  <outerBoundaryIs>
                                    <LinearRing>
                                      <coordinates>'''.format(self.name))
            
            for i in self.range.range_shape():
                # KML takes points in the form of [long],[lat],[alt]
                if i[0] is not None:
                    outfile.write("{},{},100 ".format(i[1], i[0]))
            
            outfile.write('''
                                      </coordinates>
                                    </LinearRing>
                                  </outerBoundaryIs>
                                </Polygon>
                              </Placemark>
                            </kml>'''
                            )
        