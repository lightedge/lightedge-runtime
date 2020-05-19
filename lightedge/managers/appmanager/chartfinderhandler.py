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

"""Chart Finder handler."""

import empower_core.apimanager.apimanager as apimanager


# pylint: disable=W0223
class ChartFinderHandler(apimanager.APIHandler):
    """Search charts in repos."""

    URLS = [r"/api/v1/appmanager/chartfinder/?"]

    @apimanager.validate(min_args=0, max_args=0)
    def get(self):
        """List of search results.
        Request:
            search: query for searching charts between single quotes
        Example URLs:
            GET /api/v1/appmanager/chartfinder?search='nginx'
            [
                {
                    "name": "bitnami/nginx",
                    "version": "5.2.4",
                    "app_version": "1.17.10",
                    "description": "Chart for the nginx server"
                },
                {
                    "name": "bitnami/nginx-ingress-controller",
                    "version": "5.3.19",
                    "app_version": "0.30.0",
                    "description": "Chart for the nginx Ingress controller"
                },
                {
                    "name": "joncnet/nginx-custom",
                    "version": "0.1.0",
                    "app_version": "1.0.0",
                    "description": "A content customizable nginx deployment"
                },
                {
                    "name": "bitnami/kong",
                    "version": "1.1.0",
                    "app_version": "2.0.4",
                    "description": "Kong is a scalable, open source API..."
                }
            ]
        """

        query = self.get_argument("search")
        keyword = query[1: -1]
        return self.service.chart_finder(keyword)
