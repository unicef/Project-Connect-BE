class SchoolNameDisplayAdminMixin(object):
    def get_school_name(self, obj):
        return obj.school.name

    get_school_name.short_description = 'School Name'
    get_school_name.admin_order_field = 'school__name'


class CountryNameDisplayAdminMixin(object):
    def get_country_name(self, obj):
        return obj.country.name

    get_country_name.short_description = 'Country Name'
    get_country_name.admin_order_field = 'country__name'


class LocationNameDisplayAdminMixin(object):
    def get_location_name(self, obj):
        return obj.location.name if obj.location else ''

    get_location_name.short_description = 'Location Name'
    get_location_name.admin_order_field = 'location__name'
