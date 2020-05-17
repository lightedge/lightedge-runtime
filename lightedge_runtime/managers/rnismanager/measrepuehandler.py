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

"""Exposes a RESTful interface ."""

import uuid

import empower_core.apimanager.apimanager as apimanager


# pylint: disable=W0223
class MeasRepUeHandler(apimanager.APIHandler):
    """Access the workers catalog."""

    URLS = [r"/rni/v1/subscriptions/meas_rep_ue/?",
            r"/rni/v1/subscriptions/meas_rep_ue/([a-zA-Z0-9-]*)/?"]

    @apimanager.validate(min_args=0, max_args=1)
    def get(self, *args, **kwargs):
        """Get meas_rep_ue subscriptions

        Example URLs:

            GET /rni/v1/subscriptions/meas_rep_ue

            {
              "SubscriptionLinkList": {
                "_links": {
                  "self": "http://uri/rni/v1/subscriptions/meas_rep_ue",
                  "subscription": [
                    {
                      "href": "http://uri/rni/v1/meas_rep_ue/77777",
                      "subscriptionType": "MEAS_REPORT_UE"
                    },
                    {
                      "href": "http://uri/rni/v1/meas_rep_ue/77778",
                      "subscriptionType": "MEAS_REPORT_UE"
                    }
                  ]
                }
              }
            }
        """

        subscriptions = []

        if args:

            sub = self.service.meas_rep_ue_subscriptions[uuid.UUID(args[0])]

            href = "%s/notifications/meas_rep_ue/%s" % \
                (sub.callback_reference, sub.subscription_id)

            to_add = {
                "href": href,
                "subscriptionType": "MEAS_REPORT_UE"
            }

            subscriptions.append(to_add)

        else:

            for sub in self.service.meas_rep_ue_subscriptions.values():

                href = "%s/notifications/meas_rep_ue/%s" % \
                    (sub.callback_reference, sub.subscription_id)

                to_add = {
                    "href": href,
                    "subscriptionType": "MEAS_REPORT_UE"
                }

                subscriptions.append(to_add)

        out = {
            "SubscriptionLinkList": {
                "_links": {
                    "self": "/rni/v1/subscriptions/meas_rep_ue",
                    "subscription": subscriptions
                }
            }
        }

        return out

    @apimanager.validate(returncode=201, min_args=0, max_args=1)
    def post(self, *args, **kwargs):
        """Create a new subscription.

        POST /rni/v1/subscriptions/meas_rep_ue

        {
          "MeasRepUeSubscription": {
            "callbackReference": "http://meAppClient.example.com/rni/v1/",
            "filterCriteria": {
              "appInsId": "01",
              "associateId": {
                "type": "UE_IPV4_ADDRESS",
                "value": "192.168.10.1"
              },
              "plmn": {
                "mcc": "001",
                "mnc": "01"
              },
              "cellId": "0x800000A",
              "trigger": "PERIODICAL_REPORT_STRONGEST_CELLS"
            },
            "expiryDeadline": {
              "seconds": 1577836800,
              "nanoSeconds": 0
            }
          }
        }
        """

        subscription_id = uuid.UUID(args[0]) if args else uuid.uuid4()

        subscription = \
            self.service.add_meas_rep_ue(subscription_id=subscription_id,
                                         **kwargs['MeasRepUeSubscription'])

        self.set_header("Location",
                        "/rni/v1/subscriptions/meas_rep_ue/%s" %
                        subscription.subscription_id)

    @apimanager.validate(returncode=204, min_args=0, max_args=1)
    def delete(self, *args, **kwargs):
        """Delete a subscription.

        Args:

            [0], the subscription id

        Example URLs:

            DELETE /rni/v1/subscriptions/meas_rep_ue
            DELETE /rni/v1/subscriptions/
                meas_rep_ue52313ecb-9d00-4b7d-b873-b55d3d9ada26
        """

        if args:
            self.service.rem_meas_rep_ue(uuid.UUID(args[0]))
        else:
            self.service.rem_all_meas_rep_ue()
