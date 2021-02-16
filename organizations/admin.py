""" Django admin pages for organization models """
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from organizations.models import Organization, OrganizationCourse


class ActivateDeactivateAdminMixin:
    """
    Provides the activate_selected and deactivate_select bulk actions.

    Hides the delete_selected actions; we'd much rows are deactivated than
    deleted.
    """

    HISTORY_DISCLAIMER = _(
        "Please note: as a bulk action, this will not be reflected in the model's history table."
    )

    def get_actions(self, request):
        """ Return set of Django admin actions, removing the delete action """
        actions = super().get_actions(request)

        # Remove the delete action.
        if 'delete_selected' in actions:  # pragma: no cover
            del actions['delete_selected']

        return actions

    def activate_selected(self, request, queryset):
        """ Activate the selected entries. """
        count = queryset.count()
        queryset.update(active=True)
        model_name = self.__class__.__name__

        if count == 1:
            message = _('1 {model_name} entry was successfully activated.')
        else:
            message = _('{count} {model_name} entries were successfully activated.')
        message = message.format(count=count, model_name=model_name)  # pylint: disable=no-member
        self.message_user(request, message)
        self.message_user(request, self.HISTORY_DISCLAIMER, level=messages.WARNING)

    def deactivate_selected(self, request, queryset):
        """ Deactivate the selected entries. """
        count = queryset.count()
        queryset.update(active=False)
        model_name = self.__class__.__name__

        if count == 1:
            message = _('1 {model_name} entry was successfully deactivated.')
        else:
            message = _('{count} {model_name} entries were successfully deactivated.')
        message = message.format(count=count, model_name=model_name)  # pylint: disable=no-member
        self.message_user(request, message)
        self.message_user(request, self.HISTORY_DISCLAIMER, level=messages.WARNING)

    deactivate_selected.short_description = _('Deactivate selected entries')
    activate_selected.short_description = _('Activate selected entries')


@admin.register(Organization)
class OrganizationAdmin(ActivateDeactivateAdminMixin, admin.ModelAdmin):
    """ Admin for the Organization model. """
    actions = ['activate_selected', 'deactivate_selected']
    list_display = ('name', 'short_name', 'logo', 'active',)
    list_filter = ('active',)
    ordering = ('name', 'short_name',)
    readonly_fields = ('created',)
    search_fields = ('name', 'short_name',)


@admin.register(OrganizationCourse)
class OrganizationCourseAdmin(ActivateDeactivateAdminMixin, admin.ModelAdmin):
    """ Admin for the OrganizationCourse model. """
    actions = ['activate_selected', 'deactivate_selected']
    list_display = ('course_id', 'organization', 'active')
    list_filter = ('active',)
    ordering = ('course_id', 'organization__name',)
    search_fields = ('course_id', 'organization__name', 'organization__short_name',)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Only display active Organizations.
        if db_field.name == 'organization':  # pragma: no branch
            kwargs['queryset'] = Organization.objects.filter(active=True).order_by('name')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
