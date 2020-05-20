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

"""Repo handler."""

import empower_core.apimanager.apimanager as apimanager


# pylint: disable=W0223
class RepoHandler(apimanager.APIHandler):
    """All the accounts defined in the controller."""

    URLS = [r"/api/v1/appmanager/repos",
            r"/api/v1/appmanager/repos/([a-zA-Z0-9-]*)"]

    @apimanager.validate(min_args=0, max_args=0)
    def get(self):
        """List configured repos.
        Args:
        Example URLs:
            GET /api/v1/appmanager/repos
            [
                {
                    "name": "joncnet",
                    "url": "https://raw.githubusercontent.com/joncnet/helm..."
                },
                {
                    "name": "bitnami",
                    "url": "https://charts.bitnami.com/bitnami"
                }
            ]
        """

        return self.service.repo_list()

    @apimanager.validate(returncode=201, min_args=0, max_args=0)
    def post(self, **kwargs):
        """Add a new repo.
        Args:
        Request:
            name: the name to be used for referencing to this repo
            url: the repo url
        Example URLs:
            POST /api/v1/appmanager/repos
            {
                "name": "bitnami",
                "url": "https://charts.bitnami.com/bitnami"
            }
        """

        if "name" not in kwargs or "url" not in kwargs:
            raise ValueError("name and url must be provided")

        self.service.repo_add(**kwargs)

    @apimanager.validate(returncode=204, min_args=0, max_args=0)
    def put(self):
        """Update cache for all repos.
        Args:
        Example URLs:
            PUT /api/v1/appmanager/repos
        """

        self.service.repo_update()

    @apimanager.validate(returncode=204, min_args=1, max_args=1)
    def delete(self, name):
        """Delete a repo.
        Args:
            [0]: the repo name
        Example URLs:
            DELETE /api/v1/appmanager/repos/bitnami
        """

        self.service.repo_remove(name)
