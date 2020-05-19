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
from empower_core.launcher import srv_or_die

from lightedge_runtime.managers.rnismanager.subscription import Subscription
from lightedge_runtime.managers.rnismanager.subscriptionshandler import \
    SubscriptionsHandler

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8888

SUBSCRIPTIONS = {
    "meas_rep_ue": "lightedge_runtime.workers.measrepue.measrepue"
}


class RNISManager(EService):
    """Service exposing the RNI service

    Parameters:
        ctrl_host: sd-ran controller host (optional, default: 127.0.0.1)
        ctrl_host: sd-ran controller port (optional, default: 8888)
    """

    HANDLERS = [SubscriptionsHandler]

    def __init__(self, context, service_id, ctrl_host, ctrl_port):

        super().__init__(context=context, service_id=service_id,
                         ctrl_host=ctrl_host, ctrl_port=ctrl_port)

    @property
    def subscriptions(self):
        """Return ctrl_host."""

        subscriptions = {}

        for sub_type in SUBSCRIPTIONS:
            subscriptions[sub_type] = {}

        for service in srv_or_die("envmanager").env.services.values():

            if not isinstance(service, Subscription):
                continue

            subscriptions[service.SUB_TYPE][service.service_id] = service

        return subscriptions

    def get_subscriptions_links(self, sub_type, sub_id=None):
        """Return subscriptions."""

        out = {
            "SubscriptionLinkList": {
                "_links": {
                    "self": "/rni/v1/subscriptions/%s" % sub_type,
                    "subscription": []
                }
            }
        }

        if sub_id:

            to_add = {
                "href": self.subscriptions[sub_type][sub_id].href,
                "subscriptionType": sub_type
            }

            out["SubscriptionLinkList"]["_links"]["subscription"] \
                .append(to_add)

        else:

            for subscription in self.subscriptions[sub_type].values():

                to_add = {
                    "href": subscription.href,
                    "subscriptionType": subscription.SUB_TYPE
                }

                out["SubscriptionLinkList"]["_links"]["subscription"] \
                    .append(to_add)

        return out

    def add_subscription(self, sub_id, sub_type, **kwargs):
        """Add a new subscription."""

        if sub_type not in self.subscriptions:
            raise ValueError("Invalid subscription type: %s" % sub_type)

        name = SUBSCRIPTIONS[sub_type]
        params = {
            "subscription": kwargs
        }

        env = srv_or_die("envmanager").env
        sub = env.register_service(name=name,
                                   params=params,
                                   service_id=sub_id)

        return sub

    def rem_subscription(self, sub_type, sub_id):
        """Remove subscription."""

        service_id = self.subscriptions[sub_type][sub_id].service_id

        srv_or_die("envmanager").env.unregister_service(service_id=service_id)

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
