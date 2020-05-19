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
            "MeasRepUeSubscription": {
                "callbackReference": "http://mec.client/rni/v1",
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

        loc = "/rni/v1/subscriptions/meas_rep_ue/" \
            "f48d7f17-5411-4d01-b99e-01bbc3ef49A3"

        self.post(("root", "root", loc), data, 201)

        self.get(("root", "root", loc), 200)

        self.post(("root", "root", loc), data, 400)

        self.delete(("root", "root", loc), 204)

        self.get(("root", "root", loc), 404)


if __name__ == '__main__':
    unittest.main()
