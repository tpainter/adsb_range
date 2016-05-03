from math import degrees, radians, cos, sin, asin, sqrt, atan2


class AntennaRange():

    def __init__(self, center, sectors = 360):
        
        # May not work correctly if sectors > 360
        self.num_sector = sectors
        # Sectors is [sector: (Lat, Long, Range)]
        self.sectors = { x: (None, None, 0) for x in range(sectors) }
        self.center = center
        
    def add_point(self, point):
        """
        Takes point and processes it.
        point = (lat, long, alt)
        """
        
        s = self._find_sector(point)
        r = self._find_range(point)
        
        if self.sectors[s][2] < r:
            # New farthest range
            self.sectors[s] = ( point[0], point [1], r )
        
    def _find_sector(self, point):
        """
        Returns sector that given point is located in.
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
        Returns range from center to point. Haversine formula.
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
        
        if layer == 0:
            pass        
        
        points_list = []        
        for s,p in self.sectors.iteritems():
            points_list.append( (p[0], p[1]) ) 
            
        return points_list