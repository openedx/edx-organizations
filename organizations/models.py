"""
Database ORM models managed by this Django app
Please do not integrate directly with these models!!!  This app currently
offers one programmatic API -- api.py for direct Python integration.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel


class Organization(TimeStampedModel):
    """
    An Organization is a representation of an entity which publishes/provides
    one or more courses delivered by the LMS. Organizations have a base set of
    metadata describing the organization, including id, name, and description.
    """
    name = models.CharField(max_length=255, db_index=True)
    short_name = models.CharField(max_length=255, db_index=True, verbose_name='Short Name')
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(
        upload_to='organization_logos',
        help_text=_('Please add only .PNG files for logo images. This logo will be used on certificates.'),
        null=True, blank=True, max_length=255
    )
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u"{name} ({short_name})".format(name=self.name, short_name=self.short_name)


class OrganizationCourse(TimeStampedModel):
    """
    An OrganizationCourse represents the link between an Organization and a
    Course (via course key). Because Courses are not true Open edX entities
    (in the Django/ORM sense) the modeling and integrity is limited to that
    of specifying course identifier strings in this model.
    """
    course_id = models.CharField(max_length=255, db_index=True, verbose_name='Course ID')
    organization = models.ForeignKey(Organization, db_index=True)
    active = models.BooleanField(default=True)

    class Meta(object):
        """ Meta class for this Django model """
        unique_together = (('course_id', 'organization'),)
        verbose_name = _('Link Course')
        verbose_name_plural = _('Link Courses')
