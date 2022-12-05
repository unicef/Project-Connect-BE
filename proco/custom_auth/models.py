from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.sites.models import Site
from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from templated_email import send_templated_mail

from proco.locations.models import Country


class ApplicationUser(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(
        _('username'),
        max_length=30,
        unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. This value may contain only letters, numbers ' 'and @/./+/-/_ characters.'),
            ),
        ],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True, null=True, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    countries_available = models.ManyToManyField(
        Country,
        verbose_name=_('Сountries Available'),
        blank=True,
        help_text=_('Countries to which the user has access and the ability to manage them.'),
        related_name='countries_available',
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        # Set True before inherit
        abstract = False

    def save(self, *args, **kwargs):
        if not self.email:
            # Unique constraint doesn't work correctly with empty string. So we need to forcibly set email to None.
            self.email = None

        super(ApplicationUser, self).save(*args, **kwargs)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '{0} {1}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, template_name, extra_context=None, **kwargs):
        """
        Sends an email to this User.
        """
        if not self.email:
            return

        context = {
            'user': self,
            'site': Site.objects.get_current(),
        }
        context.update(extra_context or {})

        send_templated_mail(template_name, settings.DEFAULT_FROM_EMAIL, [self.email], context, **kwargs)
