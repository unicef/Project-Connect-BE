from rest_framework.filters import BaseFilterBackend


class DateYearFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        value = request.query_params.get('year', '')
        if not value:
            return queryset

        return queryset.filter(date__year=value)


class DateWeekNumberFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        value = request.query_params.get('week', '')
        if not value:
            return queryset

        return queryset.filter(date__week=value)


class DateMonthFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        value = request.query_params.get('month', '')
        if not value:
            return queryset

        return queryset.filter(date__month=value)
