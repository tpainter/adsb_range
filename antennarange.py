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

from math import degrees, radians, cos, sin, asin, sqrt, atan2


class AntennaRange():

    def __init__(self, center, sectors = 360, layers = 0):
        self.num_sector = sectors
        self.num_layer = layers
        # Layer is [sector: (Lat, Long, Range)]
        self.layers = [None for x in range(layers + 1)]
        self.layers[0] = { x: (None, None, 0) for x in range(sectors) }
        for i in range(1, layers + 1):
            self.layers[i] = { x: (None, None, 0) for x in range(sectors) }
        
        self.center = center
        if self.center == (999.0, 999.0):
            # Coordinates of center were not given. 
            # Will try to find a reasonable guess.
            self.center_set = False
            self.points_cloud = []
            print("No center coordinates given. Will estimate.")
        else:
            self.center_set = True
        
    def add_point(self, point):
        """
        Take a point and process it.
        point = (lat, long, alt)
        """
        if not self.center_set:
            # Accumulate points until a valid center has been found.
            self._find_center(point)
            return
        
        lay = self._find_layer(point)
        s = self._find_sector(point)
        r = self._find_range(point)
        
        # Always check layer 0.
        if self.layers[0][s][2] < r:
            # New farthest range
            self.layers[0][s] = ( point[0], point [1], r )        
        
        # Then check the layer that is returned.
        if self.layers[lay][s][2] < r:
            # New farthest range
            self.layers[lay][s] = ( point[0], point [1], r )
        
    def _find_center(self, point):
        """
        If no center is given initially, find a good estimate to use.
        
        This is just the average location over a certain number of points. 
        """        
        self.points_cloud.append(point)
        
        if len(self.points_cloud) > 500:
            # Assume this is enough to get a valid point.
            lat_sum = 0
            lon_sum = 0
            for n in self.points_cloud:
                lat_sum += n[0]
                lon_sum += n[1]
                
            lat_avg = lat_sum / float(len(self.points_cloud))
            lon_avg = lon_sum / float(len(self.points_cloud))
            
            self.center = (lat_avg, lon_avg)
            self.center_set = True
            print("Using center: ({:.1f}, {:.1f})".format(self.center[0], self.center[1]))
    
    def _find_layer(self, point):
        """
        Find the layer for the altitude of the given point.
        
        Layer 0 is "all altitudes". After that, layers occur every 10,000ft.
        Last layer is unlimited in altitude.
        """
        
        if point[2] is None:
            # No altitude information
            return 0
        lay = int(point[2] / 10000)
        
        if lay >= self.num_layer:
            return self.num_layer
        else:
            return lay        
    
    def _find_sector(self, point):
        """
        Return the sector that given point is located in.
        """
        lat1 = radians(self.center[0])
        lon1 = radians(self.center[1])
        lat2 = radians(point[0])
        lon2 = radians(point[1])  
        
        dlon = lon2 - lon1
        
        y = sin(dlon) * cos(lat2)
        x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
        bearing = degrees(atan2(y, x)) #may be negative
        bearing_abs = (bearing + 360) % 360
        
        # Make bearing compatible with number of sectors.
        # i.e. if there are 720 sectors, a full circle has 720 sectors in 360 degrees.
        bearing_mult = bearing_abs * self.num_sector / 360
        
        return int(bearing_mult % self.num_sector)
        
    def _find_range(self, point):
        """
        Return the distance from center to point. Haversine formula.
        From: http://stackoverflow.com/a/4913653
        Also: http://stackoverflow.com/a/21623206
        """
        lat1 = radians(self.center[0])
        lon1 = radians(self.center[1])
        lat2 = radians(point[0])
        lon2 = radians(point[1])   
        
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        
        return c * r
        
    def range_shape(self, layer = 0):
        """
        Returns list of points that can be used to create a polygon.
        
        Can also report just the altitudes layer requested. 
        0 = All altitudes
        """
        points_list = []        
        for s,p in self.layers[layer].iteritems():
            points_list.append( (p[0], p[1]) ) 
            
        return points_list