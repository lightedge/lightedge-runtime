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

import empower_core.apimanager.apimanager as apimanager


# pylint: disable=W0223
class S1BearerInfoHandler(apimanager.APIHandler):
    """Access the workers catalog."""

    URLS = [r"/rni/v1/s1_bearer_info?"]

    @apimanager.validate(min_args=0, max_args=0)
    def get(self, *args, **kwargs):
        """Gets information on existing E-RABs

        Example URLs:

             GET /rni/v1/s1_bearer_info

            {
              "S1BearerInfo": {
                "timeStamp": {
                  "seconds": 1577836800,
                  "nanoSeconds": 0
                },
                "s1UeInfo": [
                  {
                    "tempUeId": {
                      "mmec": "0",
                      "mtmsi": "1234"
                    },
                    "associateId": [
                      {
                        "type": "1",
                        "value": "192.0.2.0"
                      },
                      {
                        "type": "3",
                        "value": "198.51.100.0"
                      }
                    ],
                    "ecgi": {
                      "plmn": {
                        "mcc": "001",
                        "mnc": "01"
                      },
                      "cellId": "0x800000A"
                    },
                    "s1BearerInfoDetailed": [
                      {
                        "erabId": 1,
                        "s1EnbInfo": {
                          "ipAddress": "192.0.2.0",
                          "tunnelId": "1111"
                        },
                        "sGwInfo": {
                          "ipAddress": "192.0.2.1",
                          "tunnelId": "2222"
                        }
                      }
                    ]
                  },
                  {
                    "tempUeId": {
                      "mmec": "0",
                      "mtmsi": "1234"
                    },
                    "associateId": {
                      "type": "1",
                      "value": "192.0.2.0"
                    },
                    "ecgi": {
                      "plmn": {
                        "mcc": "001",
                        "mnc": "01"
                      },
                      "cellId": "0x800000B"
                    },
                    "s1BearerInfoDetailed": [
                      {
                        "erabId": 2,
                        "s1EnbInfo": {
                          "ipAddress": "192.0.2.0",
                          "tunnelId": "3333"
                        },
                        "sGwInfo": {
                          "ipAddress": "192.0.2.1",
                          "tunnelId": "4444"
                        }
                      }
                    ]
                  }
                ]
              }
            }
        """

        tmp = {
          "S1BearerInfo": {
            "timeStamp": {
              "seconds": 1577836800,
              "nanoSeconds": 0
            },
            "s1UeInfo": [
              {
                "tempUeId": {
                  "mmec": "0",
                  "mtmsi": "1234"
                },
                "associateId": [
                  {
                    "type": "1",
                    "value": "192.0.2.0"
                  },
                  {
                    "type": "3",
                    "value": "198.51.100.0"
                  }
                ],
                "ecgi": {
                  "plmn": {
                    "mcc": "001",
                    "mnc": "01"
                  },
                  "cellId": "0x800000A"
                },
                "s1BearerInfoDetailed": [
                  {
                    "erabId": 1,
                    "s1EnbInfo": {
                      "ipAddress": "192.0.2.0",
                      "tunnelId": "1111"
                    },
                    "sGwInfo": {
                      "ipAddress": "192.0.2.1",
                      "tunnelId": "2222"
                    }
                  }
                ]
              },
              {
                "tempUeId": {
                  "mmec": "0",
                  "mtmsi": "1234"
                },
                "associateId": {
                  "type": "1",
                  "value": "192.0.2.0"
                },
                "ecgi": {
                  "plmn": {
                    "mcc": "001",
                    "mnc": "01"
                  },
                  "cellId": "0x800000B"
                },
                "s1BearerInfoDetailed": [
                  {
                    "erabId": 2,
                    "s1EnbInfo": {
                      "ipAddress": "192.0.2.0",
                      "tunnelId": "3333"
                    },
                    "sGwInfo": {
                      "ipAddress": "192.0.2.1",
                      "tunnelId": "4444"
                    }
                  }
                ]
              }
            ]
          }
        }

        return tmp
