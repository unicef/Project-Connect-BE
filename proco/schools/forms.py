from django import forms
from django.contrib.gis.forms import PointField
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Layout, Submit
from mapbox_location_field.forms import parse_location
from mapbox_location_field.widgets import MapAdminInput

from proco.schools.models import School


class ImportSchoolsCSVForm(forms.Form):
    csv_file = forms.FileField()
    force = forms.BooleanField(label=_('Skip rows with bad data'), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'blueForms import-csv-form'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('admin:schools_school_import_csv')
        self.helper.layout = Layout(
            Field('csv_file'),
            Field('force'),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button'),
            ),
        )


class MapboxPointField(PointField):
    def to_python(self, value):
        if isinstance(value, str):
            lng, lat = parse_location(value, first_in_order='lat')
            point = Point(x=lng, y=lat, srid=4326)
            return point
        return value


class SchoolAdminForm(forms.ModelForm):
    geopoint = MapboxPointField(widget=MapAdminInput, required=False)

    class Meta:
        model = School
        fields = forms.ALL_FIELDS
