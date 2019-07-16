"""
Add an organization through manage.py.
"""
import logging

from django.core.management import BaseCommand, CommandError

from organizations import api


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command used to add an organization.

    Example: ./manage.py add_organization hogwarts "Hogwarts School of Witchcraft and Wizardry"
    """

    def add_arguments(self, parser):
        parser.add_argument('short_name')
        parser.add_argument('name')

    def handle(self, *args, **options):
        org_options = {
            key: options[key] for key in {'short_name', 'name'}
        }

        if len(org_options['short_name']) > len(org_options['name']):
            fmt = (
                "The provided short_name ({short_name}) "
                "is longer than the provided name ({name}). "
                "You probably want to switch the order of the arguments."
            )
            raise CommandError(fmt.format(**org_options))

        created_org = api.add_organization(org_options)
        log_fmt = (
            "Created or activated organization: id={id}, "
            "short_name={short_name}, name='{name}'"
        )
        logger.info(log_fmt.format(**created_org))
