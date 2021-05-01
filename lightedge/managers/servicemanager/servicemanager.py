#!/usr/bin/env python3
#
# Copyright (c) 2021 Roberto Riggio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

"""Service manager."""

import time

from empower_core.appworker import EVERY
from empower_core.service import EService

from lightedge.managers.servicemanager.servicehandler import ServiceHandler


DEFAULT_SERVICE_TIMEOUT_S = 4


class ServiceManager(EService):
    """Service manager."""

    HANDLERS = [ServiceHandler]

    def __init__(self, context, service_id, every=EVERY):

        super().__init__(context=context, service_id=service_id, every=every)

        self.mec_services = dict()

    def loop(self):
        """Periodic control loop."""

        for mec_service_id in list(self.mec_services.keys()):
            last_seen = self.mec_services[mec_service_id]['last_seen']
            if last_seen + DEFAULT_SERVICE_TIMEOUT_S * 2 < time.time():
                self.log.info("Stale service %s.", mec_service_id)
                self.delete_service(mec_service_id)
            elif last_seen + DEFAULT_SERVICE_TIMEOUT_S < time.time():
                self.log.info("Stale service %s, removing.", mec_service_id)
                self.mec_services[mec_service_id]['state'] = 'STALE'

    def get_services(self, mec_service_id=None):
        """Get a list of registered services."""

        if mec_service_id:
            return self.mec_services[mec_service_id]

        return self.mec_services

    def upsert_service(self, mec_service_id, service):
        """Register a new service."""

        self.mec_services[mec_service_id] = service
        self.mec_services[mec_service_id]['last_seen'] = time.time()

    def delete_service(self, mec_service_id):
        """Delete a service."""

        del self.mec_services[mec_service_id]


def launch(context, service_id, every=EVERY):
    """ Initialize the module. """

    return ServiceManager(context=context, service_id=service_id, every=every)
