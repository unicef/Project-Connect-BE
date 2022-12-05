from re import findall

from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _

from proco.connection_statistics.models import SchoolWeeklyStatus
from proco.locations.models import Country
from proco.schools.models import School

external_id_max_length = School._meta.get_field('external_id').max_length
education_level_max_length = School._meta.get_field('education_level').max_length
name_max_length = School._meta.get_field('name').max_length
admin_1_name_max_length = School._meta.get_field('admin_1_name').max_length
education_level_regional_max_length = School._meta.get_field('education_level_regional').max_length
environment_max_length = School._meta.get_field('environment').max_length
address_max_length = School._meta.get_field('address').max_length
school_type_max_length = School._meta.get_field('school_type').max_length
admin_name_max_length = School._meta.get_field('admin_1_name').max_length
giga_id_school_max_length = School._meta.get_field('giga_id_school').max_length
environment_values = dict(School.ENVIRONMENT_STATUSES).keys()
required_fields = {'lat', 'lon'}


def validate_row(country: Country, data: dict):
    errors = []
    warnings = []

    missing_fields = required_fields.difference(set(data.keys()))
    if missing_fields:
        errors.append(
            _('Missing data for required column(s) {0}').format(', '.join(missing_fields)),
        )
        return None, None, errors, warnings

    school_data = {
        'country': country,
    }
    history_data = {}

    if 'school_id' in data or 'id' in data or 'external_id' in data:
        external_id = data.get('school_id', data.get('id', data.get('external_id')))
        if len(external_id) > external_id_max_length:
            errors.append(_(
                'Bad data provided for school identifier: max length of {0} characters exceeded',
            ).format(external_id_max_length))
            return None, None, errors, warnings
        school_data['external_id'] = external_id.lower()

    try:
        school_data['geopoint'] = Point(x=float(data['lon']), y=float(data['lat']))

        # if school_data['geopoint'].x == 0 and school_data['geopoint'].y == 0:
        #     errors.append(_('Bad data provided for geopoint: zero point'))
        #     return None, None, errors, warnings
    except (TypeError, ValueError):
        errors.append(_('Bad data provided for geopoint'))
        return None, None, errors, warnings

    if 'educ_level' in data or 'education_level' in data:
        education_level = data.get('educ_level', data.get('education_level'))
        # if len(edication_level) > education_level_max_length:
        #     errors.append(
        #         _('Bad data provided for education_level: max length of {0} characters exceeded').format(
        #             education_level_max_length,
        #         ))
        #     return None, None, errors, warnings
        school_data['education_level'] = education_level[:education_level_max_length]

    if 'name' in data:
        # if len(data['name']) > name_max_length:
        #     errors.append(
        #         _('Bad data provided for name: max length of {0} characters exceeded').format(
        #             name_max_length,
        #         ))
        #     return None, None, errors, warnings
        school_data['name'] = data['name'][:name_max_length]

    if 'giga_id_school' in data:
        if len(data['giga_id_school']) > giga_id_school_max_length:
            errors.append(
                _('Bad data provided for giga_id_school: max length of {0} characters exceeded').format(
                    giga_id_school_max_length,
                ))
            return None, None, errors, warnings
        school_data['giga_id_school'] = data['giga_id_school']

    if 'admin1' in data:
        # if len(data['admin1']) > admin_name_max_length:
        #     errors.append(
        #         _('Bad data provided for admin1: max length of {0} characters exceeded').format(
        #             admin_name_max_length,
        #         ))
        #     return None, None, errors, warnings
        school_data['admin_1_name'] = data['admin1'][:admin_name_max_length]
    if 'education_level_regional' in data:
        # if len(data['education_level_regional']) > education_level_regional_max_length:
        #     errors.append(
        #         _('Bad data provided for education_level_regional: max length of {0} characters exceeded').format(
        #             education_level_max_length,
        #         ))
        #     return None, None, errors, warnings
        school_data['education_level_regional'] = data['education_level_regional'][:education_level_regional_max_length]
    if 'admin2' in data:
        # if len(data['admin2']) > admin_name_max_length:
        #     errors.append(
        #         _('Bad data provided for admin2: max length of {0} characters exceeded').format(
        #             admin_name_max_length,
        #         ))
        #     return None, None, errors, warnings
        school_data['admin_2_name'] = data['admin2'][:admin_name_max_length]
    if 'admin3' in data:
        # if len(data['admin3']) > admin_name_max_length:
        #     errors.append(
        #         _('Bad data provided for admin3: max length of {0} characters exceeded').format(
        #             admin_name_max_length,
        #         ))
        #     return None, None, errors, warnings
        school_data['admin_3_name'] = data['admin3'][:admin_name_max_length]
    if 'admin4' in data:
        # if len(data['admin4']) > admin_name_max_length:
        #     errors.append(
        #         _('Bad data provided for admin4: max length of {0} characters exceeded').format(
        #             admin_name_max_length,
        #         ))
        #     return None, None, errors, warnings
        school_data['admin_4_name'] = data['admin4'][:admin_name_max_length]

    # static data
    if 'environment' in data:
        environment = data['environment'].lower()
        if environment not in environment_values:
            school_data['environment'] = School.ENVIRONMENT_STATUSES.urban
            # errors.append(
            #     _('Bad data provided for environment: should be in {0}').format(
            #         ', '.join(environment_values),
            #     ),
            # )
            # return None, None, errors, warnings
        else:
            school_data['environment'] = environment
    if 'address' in data:
        # if len(data['address']) > address_max_length:
        #     errors.append(
        #         _('Bad data provided for address: max length of {0} characters exceeded').format(
        #             address_max_length,
        #         ))
        #     return None, None, errors, warnings
        school_data['address'] = data['address'][:address_max_length]
    if 'type_school' in data:
        # if len(data['type_school']) > school_type_max_length:
        #     errors.append(
        #         _('Bad data provided for type_school: max length of {0} characters exceeded').format(
        #             school_type_max_length,
        #         ))
        #     return None, None, errors, warnings
        school_data['school_type'] = data['type_school'][:school_type_max_length]

    # historical data
    # validate integer columns first
    integer_columns = ['num_students', 'num_teachers', 'num_classroom', 'num_latrines', 'num_computers',
                       'latency_connectivity']
    for column in integer_columns:
        if column in data:
            history_data['num_students'] = validate_numeric_data(data, column)
            # if validation_error:
            #     errors.append(_(validation_error))

    # if 'num_students' in data:
    #     try:
    #         data['num_students'] = int(data['num_students'])
    #     except ValueError:
    #         errors.append(_('Bad data provided for num_students'))
    #         return None, None, errors, warnings
    #
    #     if data['num_students'] < 0:
    #         errors.append(_('Bad data provided for num_students'))
    #         return None, None, errors, warnings
    #     history_data['num_students'] = clean_number(data['num_students'])
    #
    # if 'num_teachers' in data:
    #     try:
    #         data['num_teachers'] = int(data['num_teachers'])
    #     except ValueError:
    #         errors.append(_('Bad data provided for num_teachers'))
    #         return None, None, errors, warnings
    #
    #     if data['num_teachers'] < 0:
    #         errors.append(_('Bad data provided for num_teachers'))
    #         return None, None, errors, warnings
    #     history_data['num_teachers'] = clean_number(data['num_teachers'])
    #
    # if 'num_classroom' in data:
    #     try:
    #         data['num_classroom'] = int(data['num_classroom'])
    #     except ValueError:
    #         errors.append(_('Bad data provided for num_classroom'))
    #         return None, None, errors, warnings
    #
    #     if data['num_classroom'] < 0:
    #         errors.append(_('Bad data provided for num_classroom'))
    #         return None, None, errors, warnings
    #     history_data['num_classroom'] = clean_number(data['num_classroom'])
    #
    # if 'num_latrines' in data:
    #     try:
    #         data['num_latrines'] = int(data['num_latrines'])
    #     except ValueError:
    #         errors.append(_('Bad data provided for num_latrines'))
    #         return None, None, errors, warnings
    #
    #     if data['num_latrines'] < 0:
    #         errors.append(_('Bad data provided for num_latrines'))
    #         return None, None, errors, warnings
    #     history_data['num_latrines'] = clean_number(data['num_latrines'])

    if 'electricity' in data:
        history_data['electricity_availability'] = data['electricity'].lower() in ['true', 'yes', '1']

    if 'computer_lab' in data:
        history_data['computer_lab'] = data['computer_lab'].lower() in ['true', 'yes', '1']
    # if 'num_computers' in data:
    #     try:
    #         data['num_computers'] = int(data['num_computers'])
    #     except ValueError:
    #         errors.append(_('Bad data provided for num_computers'))
    #         return None, None, errors, warnings
    #
    #     if data['num_computers'] < 0:
    #         errors.append(_('Bad data provided for num_computers'))
    #         return None, None, errors, warnings
    #     history_data['num_computers'] = clean_number(data['num_computers'])
        history_data['computer_lab'] = True
    if 'connectivity' in data:
        history_data['connectivity'] = data['connectivity'].lower() in ['true', 'yes', '1']
    if 'type_connectivity' in data:
        field_max_length = SchoolWeeklyStatus._meta.get_field('connectivity_type').max_length
        history_data['connectivity_type'] = data['type_connectivity'][:field_max_length]

        # if len(data['type_connectivity']) > (
        #     field_max_length := SchoolWeeklyStatus._meta.get_field('connectivity_type').max_length
        # ):
        #     errors.append(
        #         _('Bad data provided for type_connectivity: max length of {0} characters exceeded').format(
        #             field_max_length,
        #         ))
        #     return None, None, errors, warnings
        # history_data['connectivity_type'] = data['type_connectivity']
    if 'speed_connectivity' in data or 'connectivity_speed' in data or 'speed' in data:
        try:
            speed = float(data.get('speed_connectivity', data.get('connectivity_speed', data.get('speed'))))
            if 600 > speed > 500:
                speed = 0.5
            history_data['connectivity_speed'] = speed * (10 ** 6)  # mbps to bps
            history_data['connectivity'] = True
        except ValueError:
            errors.append(_('Bad data provided for connectivity_speed'))
            history_data['connectivity_speed'] = None
            history_data['connectivity'] = None
            # return None, None, errors, warnings
        # history_data['connectivity'] = True
    if 'coverage_availability' in data:
        history_data['coverage_availability'] = data['coverage_availability'].lower() in ['true', 'yes', '1']
    if 'coverage_type' in data:
        if data['coverage_type'].lower() in ['no service', 'no coverage', 'no']:
            if 'coverage_availability' not in data:
                history_data['coverage_availability'] = False
            history_data['coverage_type'] = SchoolWeeklyStatus.COVERAGE_NO
        else:
            field_max_length = SchoolWeeklyStatus._meta.get_field('coverage_type').max_length
            coverage_type = data['coverage_type'][:field_max_length]

            # if len(data['coverage_type']) > (
            #     field_max_length := SchoolWeeklyStatus._meta.get_field('coverage_type').max_length
            # ):
            #     errors.append(
            #         _('Bad data provided for coverage_type: max length of {0} characters exceeded').format(
            #             field_max_length,
            #         ))
            #     return None, None, errors, warnings
            if data['coverage_type'].lower() not in [type_[0] for type_ in SchoolWeeklyStatus.COVERAGE_TYPES]:
                coverage_type = None
                # errors.append(
                #     _('Bad data provided for coverage_type: {0} type does not exist').format(
                #         data['coverage_type'],
                #     ))
                # return None, None, errors, warnings
            history_data['coverage_availability'] = True
            history_data['coverage_type'] = coverage_type.lower() if coverage_type else coverage_type

    if 'latency_connectivity' in data:
        history_data['connectivity_latency'] = data['latency_connectivity']
    #     try:
    #         data['connectivity_latency'] = int(data['latency_connectivity'])
    #     except ValueError:
    #         errors.append(_('Bad data provided for latency_connectivity'))
    #         return None, None, errors, warnings
    #     if data['connectivity_latency'] < 0:
    #         errors.append(_('Bad data provided for latency_connectivity'))
    #         return None, None, errors, warnings
    #     history_data['connectivity_latency'] = data['latency_connectivity']
    if 'water' in data:
        history_data['running_water'] = data['water'].lower() in ['true', 'yes', '1']

    return school_data, history_data, errors, warnings


def validate_numeric_data(data, column_name, column_type=int, always_positive=True):
    value = data[column_name]
    try:
        value = column_type(value)
    except ValueError:
        value = None

    if value:
        if always_positive and value < 0:
            value = None
        else:
            value = clean_number(value)

    return value


def clean_number(num: [int, str]):
    if isinstance(num, str):
        num = ''.join(findall(r'[0-9]+', num))
    return num


def validate_point_distance(kd_tree, point_to_check, distance=0.5):
    # at least two points required. original point always will be closest because all of them already exists
    distances, indexes = kd_tree.query([point_to_check], p=2, k=2)
    closest_distance = distances[0][1]
    if closest_distance < distance:
        # todo: provide human readable reason of failure with information to fix
        # logger.info(data['school_data']['geopoint'].y, data['school_data']['geopoint'].x)
        # if isinstance(all_schools[indexes[0][1]], int):
        #     logger.info(School.objects.get(id=all_schools[indexes[0][1]]))
        # else:
        #     logger.info(
        #         all_schools[indexes[0][1]],
        #         all_schools[indexes[0][1]]['school_data']['geopoint'].y,
        #         all_schools[indexes[0][1]]['school_data']['geopoint'].x
        #     )
        return False
    return True
