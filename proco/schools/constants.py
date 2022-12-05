class ColorMapSchema:
    # we map both connectivity and coverage to four base colors
    GOOD = 'good'           # green
    MODERATE = 'moderate'   # yellow
    NO = 'no'               # red
    UNKNOWN = 'unknown'     # blue

    STATUS_BY_AVAILABILITY = {
        True: 'good',
        False: 'no',
        None: 'unknown',
    }
    # moderate between no and good
    STATUS_BY_CONNECTIVITY_SPEED = {
        None: 'unknown',
        0: 'no',
    }
    STATUS_BY_COVERAGE_TYPE = {
        'unknown': 'unknown',
        'no': 'no',
        '2g': 'moderate',
        '3g': 'good',
        '4g': 'good',
    }
    CONNECTIVITY_SPEED_FOR_GOOD_CONNECTIVITY_STATUS = 5 * (10 ** 6)

    def get_connectivity_status_by_connectivity_speed(self, speed):
        if connectivity_status := self.STATUS_BY_CONNECTIVITY_SPEED.get(speed):
            return connectivity_status
        elif speed >= self.CONNECTIVITY_SPEED_FOR_GOOD_CONNECTIVITY_STATUS:
            connectivity_status = 'good'
        else:
            connectivity_status = 'moderate'
        return connectivity_status

    def get_status_by_availability(self, availability):
        return self.STATUS_BY_AVAILABILITY[availability]

    def get_coverage_status_by_coverage_type(self, coverage):
        return self.STATUS_BY_COVERAGE_TYPE[coverage]


statuses_schema = ColorMapSchema()
