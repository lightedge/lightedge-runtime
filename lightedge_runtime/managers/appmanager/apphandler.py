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

"""UE Map handler."""

import empower_core.apimanager.apimanager as apimanager


# pylint: disable=W0223
class AppHandler(apimanager.APIHandler):
    """Manage the app deployments."""

    URLS = [r"/api/v1/appmanager/namespaces/([a-zA-Z0-9-]*)/apps",
            r"/api/v1/appmanager/namespaces/"
            r"([a-zA-Z0-9-]*)/apps/([a-zA-Z0-9-]*)"]

    @apimanager.validate(min_args=1, max_args=2)
    def get(self, namespace, app_name=None):
        """List entries or get detailed info about instantiated apps.
        Args:
            [0]: the namespace name
            [1]: the app name (optional)
        Example URLs:
            GET /api/v1/appmanager/namespaces/helm-sandbox/apps
            [
                {
                    "name": "app1",
                    "namespace": "helm-sandbox",
                    "revision": "1",
                    "updated": "2020-05-05 09:58:50.133770875 +0200 CEST",
                    "status": "deployed",
                    "chart": "nginx-custom-0.1.0",
                    "app_version": "1.0.0"
                },
                {
                    "name": "app2",
                    "namespace": "helm-sandbox",
                    "revision": "1",
                    "updated": "2020-05-05 09:59:12.257841891 +0200 CEST",
                    "status": "deployed",
                    "chart": "nginx-custom-0.1.0",
                    "app_version": "1.0.0"
                }
            ]
            GET /api/v1/appmanager/namespaces/helm-sandbox/apps/app1
            {
                "status": {
                    "name": "app1",
                    "info": {
                        "first_deployed": "2020-05-05T09:58:50.133770875+02:00",
                        "last_deployed": "2020-05-05T09:58:50.133770875+02:00",
                        "deleted": "",
                        "description": "Install complete",
                        "status": "deployed",
                        "notes": "Thank you for installing nginx-custom.\n..."
                    },
                    "manifest": "---\n# Source: nginx-custom/templates/web...",
                    "version": 1,
                    "namespace": "helm-sandbox"
                },
                "values": {
                    "nodeSelector": {
                        "alias": "cloud"
                    },
                    "port": 80,
                    "replicaCount": 1,
                    "useCustomContent": "Yes",
                    "websiteData": {
                        "index.html": "hello!"
                    }
                },
                "schema": {
                    "$schema": "http://json-schema.org/draft-07/schema",
                    "$id": "http://example.com/example.json",
                    "type": "object",
                    "title": "The Root Schema",
                    "description": "The root schema comprises the entire ...",
                    "default": {},
                    "additionalProperties": true,
                    "required": [
                        "useCustomContent",
                        "replicaCount",
                        "port",
                        "nodeSelector"
                    ],
                    "properties": {
                        "useCustomContent": {
                            "$id": "#/properties/useCustomContent",
                            "type": "string",
                            "title": "The Usecustomcontent Schema",
                            "description": "An explanation about the ...",
                            "default": "",
                            "examples": [
                                "Yes"
                            ]
                        },
                        "replicaCount": {
                            "$id": "#/properties/replicaCount",
                            "type": "integer",
                            "title": "The Replicacount Schema",
                            "description": "An explanation about the ...",
                            "default": 0,
                            "examples": [
                                1.0
                            ]
                        },
                        "port": {
                            "$id": "#/properties/port",
                            "type": "integer",
                            "title": "The Port Schema",
                            "description": "An explanation about the...",
                            "default": 0,
                            "examples": [
                                80.0
                            ]
                        },
                        "servicename": {
                            "$id": "#/properties/servicename",
                            "type": "string",
                            "title": "The Servicename Schema",
                            "description": "An explanation about the...",
                            "default": "",
                            "examples": [
                                "my-service-name"
                            ]
                        },
                        "nodeSelector": {
                            "$id": "#/properties/nodeSelector",
                            "type": "object",
                            "title": "The Nodeselector Schema",
                            "description": "An explanation about the ...",
                            "default": {},
                            "examples": [
                                {
                                    "alias": "cloud"
                                }
                            ],
                            "additionalProperties": true,
                            "required": [
                                "alias"
                            ],
                            "properties": {
                                "alias": {
                                    "$id": "#/properties/nodeSelector/...",
                                    "type": "string",
                                    "title": "The Alias Schema",
                                    "description": "An explanation about ...",
                                    "default": "",
                                    "examples": [
                                        "cloud"
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        """

        if app_name:
            return self.service.get_app(app_name, namespace)
        else:
            data, _ = self.service.list_apps(namespace)
            return data

    @apimanager.validate(returncode=201, min_args=1, max_args=1)
    def post(self, namespace, **kwargs):
        """Create a new app instance.
        Args:
            [0]: the namespace name
        Example URLs:
            POST /api/v1/appmanager/namespaces/helm-sandbox/apps
            {
                "release_name": "app1",
                "repochart_name": "joncnet/nginx-custom",
                "values": {
                    "useCustomContent": "Yes",
                    "websiteData": {
                        "index.html": "hello!"
                    }
                }
            }
            ...
        """

        if "release_name" not in kwargs or "repochart_name" not in kwargs:
            raise ValueError("release_name and repochart_name must be provided")

        values = kwargs['values'] if 'values' in kwargs else {}

        service_endpoints = []
        if "service_endpoints" in kwargs:
            service_endpoints = kwargs["service_endpoints"]

        data = self.service.create_app(kwargs["release_name"], kwargs["repochart_name"],
                                         namespace, values, service_endpoints)
        return data

    @apimanager.validate(returncode=204, min_args=2, max_args=2)
    def put(self, namespace, app_name, **kwargs):
        """Update an app instance.
        Args:
            [0]: the namespace name
            [1]: the app name
        Example URLs:
            PUT /api/v1/appmanager/namespaces/helm-sandbox/apps/app1
            {
                "values": {
                    "servicename": "final"
                }
            }
            ...
        """

        values = kwargs['values'] if 'values' in kwargs else {}
        self.service.update_app(app_name, namespace, values)

    @apimanager.validate(returncode=204, min_args=1, max_args=2)
    def delete(self, namespace, app_name=None):
        """Delete an app instance.
        Args:
            [0]: the namespace name
            [0]: the app name (optional)
        Example URLs:
            DELETE /api/v1/appmanager/namespaces/helm-sandbox/apps
            DELETE /api/v1/appmanager/namespaces/helm-sandbox/apps/app1
        """

        if app_name:
            self.service.delete_app(app_name, namespace)
