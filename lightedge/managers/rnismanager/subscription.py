#!/usr/bin/env python3
#
# Copyright (c) 2020 Roberto Riggio
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

"""A genercic subscription."""

from empower_core.worker import EWorker


class Subscription(EWorker):
    """A generci subscription."""

    SUB_TYPE = None
    SUB_CONFIG = None
    MODULES = []

    def __init__(self, context, service_id, every, subscription):

        super().__init__(context=context, service_id=service_id, every=every,
                         subscription=subscription)

    @property
    def callback_reference(self):
        """Return callback_reference."""

        return self.subscription[self.SUB_CONFIG]['callbackReference']

    @property
    def expiry_deadline(self):
        """Return expiry_deadline."""

        return self.subscription[self.SUB_CONFIG]['expiryDeadline']

    @property
    def subscription(self):
        """Return subscription."""

        return self.params["subscription"]

    @subscription.setter
    def subscription(self, value):
        """Set subscription."""

        if self.SUB_CONFIG not in value:
            raise ValueError("Unable to find '%s'" % self.SUB_CONFIG)

        required_params = ['callbackReference', 'expiryDeadline']

        for param in required_params:
            if param not in value[self.SUB_CONFIG]:
                raise ValueError("Unable to find '%s'")

        self.params["subscription"] = value

    @property
    def href(self):
        """Return href."""

        return "%s/notifications/%s/%s" % \
            (self.callback_reference, self.SUB_TYPE, self.service_id)
