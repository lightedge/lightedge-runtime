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

"""Exposes a RESTful interface ."""

import uuid

import empower_core.apimanager.apimanager as apimanager


# pylint: disable=W0223
class SubscriptionsCallbackHandler(apimanager.APIHandler):
    """Access the RNI subscriptions."""

    URLS = [r"/rni/v2/subscriptions/([a-zA-Z0-9-]*)/ch/?"]

    @apimanager.validate(returncode=201, min_args=1, max_args=1)
    def post(self, *args, **kwargs):
        """Handle an incoming callback."""

        service_id = uuid.UUID(args[0])

        self.service.handle_callback(service_id, kwargs)
