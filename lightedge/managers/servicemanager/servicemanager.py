#!/usr/bin/env python3
#
# Copyright (c) 2020 Giovanni Baggio
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

import requests

from empower_core.service import EService

from lightedge.managers.servicemanager.servicehandler import ServiceHandler


DEFAULT_SERVICE_TIMEOUT = 3000


class ServiceManager(EService):
    """Service manager."""

    HANDLERS = [ServiceHandler]

    def __init__(self, context, service_id, service_timeout):

        super().__init__(context=context, service_id=service_id,
                         service_timeout=service_timeout)

        self.services = dict()

    def send_request(self, service_name, timeout=None, **kwargs):
        """Send request to service."""

        if service_name not in self.services:
            raise KeyError("Service name %s not found" % service_name)
        service = self.services[service_name]
        if not timeout:
            timeout = service["timeout"]

        response = requests.put(service["url"], timeout=timeout, json=kwargs)
        if response.status_code != service["expected_code"]:
            raise ValueError(response.content)

        return response.json()

    def get_services(self, service_name=None):
        """Get a list of registered services."""

        if service_name:
            return self.services[service_name]

        return list(self.services.values())

    def add_service(self, service):
        """Register a new service."""

        service_name = service["name"]
        if service_name in self.services:
            raise ValueError("This service already exists")

        if "expected_code" not in service:
            service["expected_code"] = 200
        self.services[service_name] = service

    def update_service(self, service_name, service):
        """Update the information for a registered service."""

        if service_name != service["name"]:
            raise ValueError("Service name in url must coincide with the body")
        self.services[service_name] = service

        return self.services[service_name]

    def delete_service(self, service_name):
        """Delete a service."""

        del self.services[service_name]

    @property
    def service_timeout(self):
        """Return service_timeout."""

        return self.params["service_timeout"]

    @service_timeout.setter
    def service_timeout(self, value):
        """Set service_timeout."""

        self.params["helm"] = value


def launch(context, service_id, service_timeout=DEFAULT_SERVICE_TIMEOUT):
    """ Initialize the module. """

    return ServiceManager(context=context, service_id=service_id,
                          service_timeout=service_timeout)
