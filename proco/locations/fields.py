import json

from rest_framework.fields import Field


class GeoPointCSVField(Field):
    def to_representation(self, value):
        point_json = json.loads(value.json)
        point_coordinates = point_json['coordinates']

        point = f'{point_coordinates[0]}: {point_coordinates[1]}'

        return point

    def to_internal_value(self, data):
        return NotImplemented
