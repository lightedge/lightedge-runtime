#!/usr/bin/env python3
#
# Copyright (c) 2019 Roberto Riggio
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

"""RNIS Manager."""

from empower_core.service import EService

from lightedge_runtime.managers.rnismanager.measrepue import MeasRepUe
from lightedge_runtime.managers.rnismanager.measrepuehandler import \
    MeasRepUeHandler

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8888


class RNISManager(EService):
    """Service exposing the RNI service

    Parameters:
        ctrl_host: sd-ran controller host (optional, default: 127.0.0.1)
        ctrl_host: sd-ran controller port (optional, default: 8888)
    """

    HANDLERS = [MeasRepUeHandler]

    def __init__(self, context, service_id, ctrl_host, ctrl_port):

        super().__init__(context=context, service_id=service_id,
                         ctrl_host=ctrl_host, ctrl_port=ctrl_port)

        self.meas_rep_ue_subscriptions = {}

    def add_meas_rep_ue(self, subscription_id, **kwargs):
        """Add a new meas_rep_ue subscription."""

        if subscription_id in self.meas_rep_ue_subscriptions:
            raise ValueError("Subscription %s already defined" %
                             subscription_id)

        self.meas_rep_ue_subscriptions[subscription_id] = \
            MeasRepUe(subscription_id=subscription_id, **kwargs)

        return self.meas_rep_ue_subscriptions[subscription_id]

    def rem_meas_rep_ue(self, subscription_id):
        """Add a new meas_rep_ue subscription."""

        if subscription_id not in self.meas_rep_ue_subscriptions:
            raise KeyError("Subscription %s not registered" %
                           subscription_id)

        del self.meas_rep_ue_subscriptions[subscription_id]

    def rem_all_meas_rep_ue(self):
        """Remove all devices."""

        for subscription_id in list(self.meas_rep_ue_subscriptions):
            self.rem_meas_rep_ue(subscription_id)

    @property
    def ctrl_host(self):
        """Return ctrl_host."""

        return self.params["ctrl_host"]

    @ctrl_host.setter
    def ctrl_host(self, value):
        """Set ctrl_host."""

        if "ctrl_host" in self.params and self.params["ctrl_host"]:
            raise ValueError("Param ctrl_host can not be changed")

        self.params["ctrl_host"] = str(value)

    @property
    def ctrl_port(self):
        """Return ctrl_port."""

        return self.params["ctrl_port"]

    @ctrl_port.setter
    def ctrl_port(self, value):
        """Set host."""

        if "ctrl_port" in self.params and self.params["ctrl_port"]:
            raise ValueError("Param ctrl_port can not be changed")

        self.params["ctrl_port"] = int(value)


def launch(context, service_id, ctrl_host=DEFAULT_HOST,
           ctrl_port=DEFAULT_PORT):
    """ Initialize the module. """

    return RNISManager(context, service_id, ctrl_host, ctrl_port)
