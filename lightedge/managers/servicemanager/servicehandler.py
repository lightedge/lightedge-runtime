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

"""Service handler."""

import uuid

import empower_core.apimanager.apimanager as apimanager


# pylint: disable=W0223
class ServiceHandler(apimanager.APIHandler):
    """Handle services."""

    URLS = [r"/api/v1/services/?",
            r"/api/v1/services/([a-zA-Z0-9-]*)/?"]

    @apimanager.validate(min_args=0, max_args=1)
    def get(self, *args):
        """List entries in the Match Map.
        Args:
            [0]: the service UUID
        Example URLs:
            GET /api/v1/services
            [
                {
                    "serInstanceId": "ad13ffb8-a7ed-423d-b758-afdf9c4d5369",
                    "serName": "Radio Network Information Service",
                    "serCategory": {
                        "href": "/rni/v2/",
                        "id": "rni",
                        "name": "Radio Network Information Service",
                        "version": "2.0"
                    },
                    "version": "1.0",
                    "state": "ACTIVE",
                    "serializer": "JSON",
                },
                {
                    "serInstanceId": "ad13ffb8-a7ed-423d-b758-afdf9c4d5371",
                    "serName": "WLAN Information API",
                    "serCategory": {
                        "href": "/wia/v1/",
                        "id": "WIA",
                        "name": "WLAN Information API",
                        "version": "1.0"
                    },
                    "version": "1.0",
                    "state": "ACTIVE",
                    "serializer": "JSON",
                },
            ]
            GET /api/v1/services/ad13ffb8-a7ed-423d-b758-afdf9c4d5369
            {
                "serInstanceId": "ad13ffb8-a7ed-423d-b758-afdf9c4d5369",
                "serName": "Radio Network Information Service",
                "serCategory": {
                    "href": "/rni/v2/",
                    "id": "rni",
                    "name": "Radio Network Information Service",
                    "version": "2.0"
                },
                "version": "1.0",
                "state": "ACTIVE",
                "serializer": "JSON",
            }
        """

        if args:
            return self.service.get_services(uuid.UUID(args[0]))

        return self.service.get_services()

    @apimanager.validate(returncode=201, min_args=0, max_args=1)
    def post(self, *args, **kwargs):
        """Add a new service.
        Example URLs:
            POST /api/v1/servicemanager
            {
              "serInstanceId": "ad13ffb8-a7ed-423d-b758-afdf9c4d5369",
              "serName": "Radio Network Information Service",
              "serCategory": {
                "href": "/rni/v2/",
                "id": "rni",
                "name": "Radio Network Information Service",
                "version": "2.0"
              },
              "version": "1.0",
              "state": "ACTIVE",
              "serializer": "JSON",
            }
        """

        mec_service_id = uuid.UUID(args[0]) if args else uuid.uuid4()

        return self.service.upsert_service(mec_service_id, kwargs)

    @apimanager.validate(returncode=204, min_args=1, max_args=1)
    def put(self, *args, **kwargs):
        """Update a service.
        Args:
            [0]: the service UUID
        Example URLs:
            PUT /api/v1/servicemanager/ad13ffb8-a7ed-423d-b758-afdf9c4d5369
            {
              "serInstanceId": "ad13ffb8-a7ed-423d-b758-afdf9c4d5369",
              "serName": "Radio Network Information Service",
              "serCategory": {
                "href": "/rni/v2/",
                "id": "rni",
                "name": "Radio Network Information Service",
                "version": "2.0"
              },
              "version": "1.0",
              "state": "ACTIVE",
              "serializer": "JSON",
            }
        """

        return self.service.upsert_service(uuid.UUID(args[0]), kwargs)

    @apimanager.validate(returncode=204, min_args=1, max_args=1)
    def delete(self, args):
        """Delete a service.
        Args:
            [0]: the service UUID
        Example URLs:
            DELETE /api/v1/servicemanager/ad13ffb8-a7ed-423d-b758-afdf9c4d5369
        """

        self.service.delete_service(uuid.UUID(args[0]))
