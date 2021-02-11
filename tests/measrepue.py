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

"""Accounts unit tests."""

import unittest

from .common import BaseTest


class TestMeasRepUe(BaseTest):
    """MeasRepUe unit tests."""

    def test_create_meas_rep_ue(self):
        """test_create_existing_user."""

        data = {
            "callbackReference": "http://127.0.0.1:5000/callback",
            "filterCriteriaAssocTri": {
                "appInstanceId": "069898f8-5e71-4010-94d2-29982ecad9dd",
                "associateId": [{
                    "type": "IMSI",
                    "value": "222930100001114"
                }],
                "ecgi": {
                  "cellId": "0x03",
                  "plmn": {
                    "mcc": "222",
                    "mnc": "93"
                  }
                },
                "trigger": ["PERIODICAL_REPORT_STRONGEST_CELLS"]
            },
            "expiryDeadline": {
                "seconds": 1577836800,
                "nanoSeconds": 0
            },
            "subscriptionType": "MeasRepUeSubscription"
        }

        loc = "/rni/v2/subscriptions/fa0141c0-d8f6-4249-9d7d-f7dd35be3e3a"

        self.post(("root", "root", loc), data, 201)

        return

        self.get(("root", "root", loc), 200)

        self.post(("root", "root", loc), data, 400)

        self.delete(("root", "root", loc), 204)

        self.get(("root", "root", loc), 404)


if __name__ == '__main__':
    unittest.main()
