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
class SubscriptionsHandler(apimanager.APIHandler):
    """Access the RNI subscriptions."""

    URLS = [r"/rni/v1/subscriptions/([a-zA-Z0-9_]*)/?",
            r"/rni/v1/subscriptions/([a-zA-Z0-9_]*)/([a-zA-Z0-9-]*)/?"]

    @apimanager.validate(min_args=1, max_args=2)
    def get(self, *args, **kwargs):
        """Get the subscriptions

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

        sub_type = args[0]
        sub_id = uuid.UUID(args[1]) if len(args) > 1 else None

        return self.service.get_subscriptions_links(sub_type, sub_id)

    @apimanager.validate(returncode=201, min_args=1, max_args=2)
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

        sub_type = args[0]
        sub_id = uuid.UUID(args[1]) if len(args) > 1 else uuid.uuid4()

        sub = self.service.add_subscription(sub_type=sub_type, sub_id=sub_id,
                                            **kwargs)

        self.set_header("Location", "/rni/v1/subscriptions/%s/%s" %
                        (sub.SUB_TYPE, sub.service_id))

    @apimanager.validate(returncode=204, min_args=2, max_args=2)
    def delete(self, *args, **kwargs):
        """Delete a subscription.

        Args:

            [0], the subscription id

        Example URLs:

            DELETE /rni/v1/subscriptions/
                meas_rep_ue/52313ecb-9d00-4b7d-b873-b55d3d9ada26
        """

        sub_type = args[0]
        sub_id = uuid.UUID(args[1])

        self.service.rem_subscription(sub_type=sub_type, sub_id=sub_id)
