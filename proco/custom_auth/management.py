def create_group_data_owner(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission

    group, created = Group.objects.get_or_create(
        name='Data Owner',
    )
    if created:
        permissions = Permission.objects.filter(
            codename__in=(
                'view_countrydailystatus',
                'view_countryweeklystatus',
                'view_realtimeconnectivity',
                'view_schooldailystatus',
                'view_schoolweeklystatus',
                'view_country',
                'view_school',

                'add_fileimport',
                'change_fileimport',
                'delete_fileimport',
                'view_fileimport',
            ),
        )
        group.permissions.set(permissions)
