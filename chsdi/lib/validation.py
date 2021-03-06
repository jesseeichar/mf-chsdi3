# -*- coding: utf-8 -*-

import re
import types
import pyramid.httpexceptions as exc
from chsdi.lib.helpers import check_even

from chsdi.esrigeojsonencoder import loads
from shapely.geometry import asShape


class MapNameValidation(object):

    def hasMap(self, db, mapName):
        from chsdi.models.bod import Topics
        availableMaps = [q[0] for q in db.query(Topics.id)]
        # FIXME add this info in DB
        availableMaps.append('all')
        availableMaps.append('api')
        availableMaps.append('api-free')
        availableMaps.append('api-notfree')
        availableMaps.append('swissmaponline')

        if mapName not in availableMaps:
            raise exc.HTTPBadRequest('The map you provided does not exist')


class MapServiceValidation(MapNameValidation):

    def __init__(self):
        super(MapServiceValidation, self).__init__()
        self._geometry = None
        self._geometryType = None
        self._returnGeometry = None
        self._imageDisplay = None
        self._mapExtent = None
        self._tolerance = None
        self._timeInstant = None
        self._layers = None
        self._layer = None
        self._searchText = None
        self._searchField = None
        self.esriGeometryTypes = (
            'esriGeometryPoint',
            'esriGeometryPolyline',
            'esriGeometryPolygon',
            'esriGeometryEnvelope'
        )

    @property
    def geometry(self):
        return self._geometry

    @property
    def geometryType(self):
        return self._geometryType

    @property
    def returnGeometry(self):
        return self._returnGeometry

    @property
    def imageDisplay(self):
        return self._imageDisplay

    @property
    def mapExtent(self):
        return self._mapExtent

    @property
    def tolerance(self):
        return self._tolerance

    @property
    def timeInstant(self):
        return self._timeInstant

    @property
    def models(self):
        return self._models

    @property
    def layers(self):
        return self._layers

    @property
    def layer(self):
        return self._layer

    @property
    def searchField(self):
        return self._searchField

    @geometry.setter
    def geometry(self, value):
        if value is None:
            raise exc.HTTPBadRequest('Please provide the parameter geometry  (Required)')
        else:
            try:
                self._geometry = loads(value)
            except ValueError:
                raise exc.HTTPBadRequest('Please provide a valide geometry')

    @geometryType.setter
    def geometryType(self, value):
        if value is None:
            raise exc.HTTPBadRequest('Please provide the parameter geometryType  (Required)')
        if value not in self.esriGeometryTypes:
            raise exc.HTTPBadRequest('Please provide a valid geometry type')
        self._geometryType = value

    @returnGeometry.setter
    def returnGeometry(self, value):
        if value is False or value == 'false':
            self._returnGeometry = False
        else:
            self._returnGeometry = True

    @imageDisplay.setter
    def imageDisplay(self, value):
        if value is None:
            raise exc.HTTPBadRequest('Please provide the parameter imageDisplay  (Required)')
        value = value.split(',')
        if len(value) != 3:
            raise exc.HTTPBadRequest('Please provide the parameter imageDisplay in a comma separated list of 3 arguments (width,height,dpi)')
        try:
            self._imageDisplay = map(float, value)
        except ValueError:
            raise exc.HTTPBadRequest('Please provide numerical values for the parameter imageDisplay')

    @mapExtent.setter
    def mapExtent(self, value):
        if value is None:
            raise exc.HTTPBadRequest('Please provide the parameter mapExtent  (Required)')
        else:
            try:
                feat = loads(value)
                self._mapExtent = asShape(feat)
            except ValueError:
                raise exc.HTTPBadRequest('Please provide numerical values for the parameter mapExtent')

    @tolerance.setter
    def tolerance(self, value):
        if value is None:
            raise exc.HTTPBadRequest('Please provide the parameter tolerance (Required)')
        try:
            self._tolerance = float(value)
        except ValueError:
            raise exc.HTTPBadRequest('Please provide an integer value for the pixel tolerance')

    @timeInstant.setter
    def timeInstant(self, value):
        if value is not None:
            if len(value) != 4:
                raise exc.HTTPBadRequest('Only years are supported as timeInstant parameter')
            try:
                self._timeInstant = int(value)
            except ValueError:
                raise exc.HTTPBadRequest('Please provide an integer for the parameter timeInstant')
        else:
            self._timeInstant = value

    @layers.setter
    def layers(self, value):
        if value is None:
            raise exc.HTTPBadRequest('Please provide a parameter layers')
        if value == 'all':
            self._layers = value
        else:
            try:
                layers = value.split(':')[1]
                self._layers = layers.split(',')
            except:
                exc.HTTPBadRequest('There is an error in the parameter layers')

    @layer.setter
    def layer(self, value):
        if value is None:
            raise exc.HTTPBadRequest('Please provide a parameter layer')
        if len(value.split(',')) > 1:
            raise exc.HTTPBadRequest('You can provide only one layer at a time')
        self._layer = value

    @searchField.setter
    def searchField(self, value):
        if value is None:
            raise exc.HTTPBadRequest('Please provide a searchField')
        if len(value.split(',')) > 1:
            raise exc.HTTPBadRequest('You can provide only one searchField at a time')
        self._searchField = value


class HeightValidation(object):

    def __init__(self):
        self._lon = None
        self._lat = None
        self._layers = None

    @property
    def lon(self):
        return self._lon

    @property
    def lat(self):
        return self._lat

    @property
    def layers(self):
        return self._layers

    @lon.setter
    def lon(self, value):
        if value is None:
            raise exc.HTTPBadRequest("Missing parameter 'easting'/'lon'")
        try:
            self._lon = float(value)
        except ValueError:
            raise exc.HTTPBadRequest("Please provide numerical values for the parameter 'easting'/'lon'")

    @lat.setter
    def lat(self, value):
        if value is None:
            raise exc.HTTPBadRequest("Missing parameter 'norhting'/'lat'")
        try:
            self._lat = float(value)
        except ValueError:
            raise exc.HTTPBadRequest("Please provide numerical values for the parameter 'northing'/'lat'")

    @layers.setter
    def layers(self, value):
        if not isinstance(value, list):
            value = value.split(',')
            for i in value:
                if i not in ('DTM25', 'DTM2', 'COMB'):
                    raise exc.HTTPBadRequest("Please provide a valid name for the elevation model DTM25, DTM2 or COMB")
        self._layers = value


class ProfileValidation(object):

    def __init__(self):
        self._linestring = None
        self._layers = None
        self._nb_points = None
        self._ma_offset = None

    @property
    def linestring(self):
        return self._linestring

    @property
    def layers(self):
        return self._layers

    @property
    def nb_points(self):
        return self._nb_points

    @property
    def ma_offset(self):
        return self._ma_offset

    @linestring.setter
    def linestring(self, value):
        import geojson
        if value is None:
            raise exc.HTTPBadRequest("Missing parameter geom")
        try:
            geom = geojson.loads(value, object_hook=geojson.GeoJSON.to_instance)
        except:
            raise exc.HTTPBadRequest("Error loading geometry in JSON string")
        try:
            shape = asShape(geom)
        except:
            raise exc.HTTPBadRequest("Error converting JSON to Shape")
        try:
            shape.is_valid
        except:
            raise exc.HTTPBadRequest("Invalid Linestring syntax")

        self._linestring = shape

    @layers.setter
    def layers(self, value):
        if value is None:
            self._layers = ['DTM25']
        else:
            value = value.split(',')
            for i in value:
                if i not in ('DTM25', 'DTM2', 'COMB'):
                    raise exc.HTTPBadRequest("Please provide a valid name for the elevation model DTM25, DTM2 or COMB")
            value.sort()
            self._layers = value

    @nb_points.setter
    def nb_points(self, value):
        if value is None:
            self._nb_points = 200
        else:
            try:
                self._nb_points = int(value)
            except ValueError:
                raise exc.HTTPBadRequest("Please provide a numerical value for the parameter 'NbPoints'/'nb_points'")

    @ma_offset.setter
    def ma_offset(self, value):
        if value is None:
            self._ma_offset = 3
        else:
            try:
                self._ma_offset = int(value)
            except ValueError:
                raise exc.HTTPBadRequest("Please provide a numerical value for the parameter 'offset'")


class SearchValidation(MapNameValidation):

    def __init__(self):
        super(SearchValidation, self).__init__()
        self._searchText = None
        self._featureIndexes = None
        self._timeInstant = None
        self._timeEnabled = None
        self._bbox = None
        self._returnGeometry = None

    @property
    def searchText(self):
        return self._searchText

    @property
    def featureIndexes(self):
        return self._featureIndexes

    @property
    def timeEnabled(self):
        return self._timeEnabled

    @property
    def bbox(self):
        return self._bbox

    @property
    def timeInstant(self):
        return self._timeInstant

    @property
    def returnGeometry(self):
        return self._returnGeometry

    @featureIndexes.setter
    def featureIndexes(self, value):
        if value is not None and value != '':
            # SphinxSearch does not support indices longer than 64
            # characters, that's why we have to hardcode here to
            # something below 64 (indices are prepared with this name)
            value = value.replace('ch.swisstopo.geologie-hydrogeologische_karte-grundwasservulnerabilitaet', 'ch_swisstopo_geologie-hydro_karte-grundwasservul')
            value = value.replace('ch.swisstopo.geologie-hydrogeologische_karte-grundwasservorkommen', 'ch_swisstopo_geologie-hydro_karte-grundwasservor')
            value = value.replace('.', '_')
            self._featureIndexes = value.split(',')

    @timeEnabled.setter
    def timeEnabled(self, value):
        if value is not None and value != '':
            values = value.split(',')
            result = []
            for val in values:
                result.append(True if val.lower() in ['true', 't', '1'] else False)
            self._timeEnabled = result

    @searchText.setter
    def searchText(self, value):
        if value is None:
            raise exc.HTTPBadRequest("Please provide a search text")
        searchTextList = value.split(' ')
        # Remove empty strings
        searchTextList = filter(None, searchTextList)
        self._searchText = searchTextList

    @bbox.setter
    def bbox(self, value):
        if value is not None and value != '':
            values = value.split(',')
            if len(values) != 4:
                raise exc.HTTPBadRequest("Please provide 4 coordinates in a comma separated list")
            try:
                values = map(float, values)
            except ValueError:
                raise exc.HTTPBadRequest("Please provide numerical values for the parameter bbox")
            # Swiss extent
            if values[0] >= 420000 and values[1] >= 30000:
                if values[0] < values[1]:
                    raise exc.HTTPBadRequest("The first coordinate must be higher than the second")
            if values[2] >= 420000 and values[3] >= 30000:
                if values[2] < values[3]:
                    raise exc.HTTPBadRequest("The third coordinate must be higher than the fourth")
            self._bbox = values

    @timeInstant.setter
    def timeInstant(self, value):
        if value is not None:
            if len(value) != 4:
                raise exc.HTTPBadRequest('Only years are supported as timeInstant parameter')
            try:
                self._timeInstant = int(value)
            except ValueError:
                raise exc.HTTPBadRequest('Please provide an integer for the parameter timeInstant')
        else:
            self._timeInstant = value

    @returnGeometry.setter
    def returnGeometry(self, value):
        if value is False or value == 'false':
            self._returnGeometry = False
        else:
            self._returnGeometry = True
