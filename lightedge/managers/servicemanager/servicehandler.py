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

"""Service handler."""

import empower_core.apimanager.apimanager as apimanager


# pylint: disable=W0223
class ServiceHandler(apimanager.APIHandler):
    """Handle services."""

    URLS = [r"/api/v1/servicemanager/?",
            r"/api/v1/servicemanager/([a-zA-Z0-9-]*)/?"]

    @apimanager.validate(min_args=0, max_args=1)
    def get(self, service_name=None):
        """List entries in the Match Map.
        Args:
            [0]: the service name
        Example URLs:
            GET /api/v1/servicemanager
            [
                {
                    "name": "service1",
                    "description": "description of service1",
                    "url": "http://localhost:8000/double_endpoint",
                    "timeout": 3000,
                    "expected_code": 200
                },
                {
                    "name": "service2",
                    "description": "description of service2",
                    "url": "http://localhost:8000/content_endpoint",
                    "timeout": 3000,
                    "expected_code": 200
                }
            ]
            GET /api/v1/servicemanager/service1
            {
                "name": "service1",
                "description": "description of service1",
                "url": "http://localhost:8000/double_endpoint",
                "timeout": 3000,
                "expected_code": 200
            }
        """

        return self.service.get_services(service_name)

    @apimanager.validate(returncode=201, min_args=0, max_args=0)
    def post(self, **kwargs):
        """Add a new service.
        Example URLs:
            POST /api/v1/servicemanager
            {
                "name": "service1",
                "description": "description of service1",
                "url": "http://localhost:8000/double_endpoint",
                "timeout": 3000
            }
        """

        return self.service.add_service(kwargs)

    @apimanager.validate(returncode=204, min_args=1, max_args=1)
    def put(self, service_name, **kwargs):
        """Update a service.
        Args:
            [0]: the service name
        Example URLs:
            PUT /api/v1/servicemanager/service1
            {
                "name": "service1",
                "description": "description of service1",
                "url": "http://localhost:1234"
            }
        """

        return self.service.update_service(service_name, kwargs)

    @apimanager.validate(returncode=204, min_args=1, max_args=1)
    def delete(self, service_name):
        """Delete a service.
        Args:
            [0]: the service name
        Example URLs:
            DELETE /api/v1/servicemanager/service1
        """

        self.service.delete_service(service_name)
