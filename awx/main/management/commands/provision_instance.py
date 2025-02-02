# Copyright (c) 2015 Ansible, Inc.
# All Rights Reserved

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from awx.main.models import Instance


class Command(BaseCommand):
    """
    Internal tower command.
    Register this instance with the database for HA tracking.
    """

    help = 'Add instance to the database. ' 'Specify `--hostname` to use this command.'

    def add_arguments(self, parser):
        parser.add_argument('--hostname', dest='hostname', type=str, help='Hostname used during provisioning')
        parser.add_argument('--node_type', type=str, default="hybrid", choices=["control", "execution", "hybrid"], help='Instance Node type')

    def _register_hostname(self, hostname, node_type):
        if not hostname:
            return
        (changed, instance) = Instance.objects.register(uuid=self.uuid, hostname=hostname, node_type=node_type)
        if changed:
            print('Successfully registered instance {}'.format(hostname))
        else:
            print("Instance already registered {}".format(instance.hostname))
        self.changed = changed

    @transaction.atomic
    def handle(self, **options):
        if not options.get('hostname'):
            raise CommandError("Specify `--hostname` to use this command.")
        self.uuid = settings.SYSTEM_UUID
        self.changed = False
        self._register_hostname(options.get('hostname'), options.get('node_type'))
        if self.changed:
            print('(changed: True)')
