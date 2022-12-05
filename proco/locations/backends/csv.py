import csv
from datetime import datetime

from django.http import HttpResponse


class SchoolsCSVWriterBackend:
    def __init__(self, serializer, country):
        self.serializer = serializer
        self.filename = self.get_filename(country)

    def get_filename(self, country):
        date = datetime.now().date().strftime('%Y-%m-%d')
        return f'{country.name}_schools_{date}.csv'

    def writeheader(self, writer, header, labels):
        header = dict(zip(header, labels))
        writer.writerow(header)

    def remove_underscore(self, field):
        return field.replace('_', ' ')

    def write(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.filename}"'

        csv_header = self.serializer.child.__class__.Meta.fields
        labels = [self.remove_underscore(field.title()) for field in csv_header]
        writer = csv.DictWriter(response, fieldnames=csv_header)
        self.writeheader(writer, csv_header, labels)

        for row in self.serializer.data:
            writer.writerow(row)

        return response
