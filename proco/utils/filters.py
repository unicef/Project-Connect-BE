from django.db.models import F

from rest_framework.filters import OrderingFilter


class NullsAlwaysLastOrderingFilter(OrderingFilter):
    """ Use Django 1.11 nulls_last feature to force nulls to bottom in all orderings. """
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            f_ordering = []
            for o in ordering:
                if not o:
                    continue
                if o[0] == '-':
                    f_ordering.append(F(o[1:]).desc(nulls_last=True))
                else:
                    f_ordering.append(F(o).asc(nulls_last=True))

            return queryset.order_by(*f_ordering)

        return queryset
