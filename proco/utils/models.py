from django.db import connections, models


class ApproxQuerySet(models.QuerySet):
    # calculate queryset size approximately based on pg statistics
    def count(self, approx=True):
        if approx and not self.query.where:
            cursor = connections[self.db].cursor()
            cursor.execute(
                'SELECT reltuples::int FROM pg_class WHERE relname = %s;',
                (self.model._meta.db_table,),
            )
            return cursor.fetchall()[0][0]
        else:
            return super().count()

    def __len__(self):
        if not self.query.where:
            return self.count()
        return super().__len__()
