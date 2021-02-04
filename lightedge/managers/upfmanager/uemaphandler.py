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

"""UE Map handler."""

# import lightedge.managers.apimanager.apimanager as apimanager
import empower_core.apimanager.apimanager as apimanager

# pylint: disable=W0223
class UEMapHandler(apimanager.APIHandler):
    """All the accounts defined in the controller."""

    URLS = [r"/api/v1/uemap/?", r"/upf/v1/uemap/([0-9.]*)"]

    @apimanager.validate(min_args=0, max_args=1)
    def get(self, ue_ip=None):
        """List entries in the UE Map.

        Args:

            [0]: the UE Ip

        Example URLs:

            GET /upf/v1/uemap

            {
                "10.10.0.3": {
                    "ue_ip": "10.10.0.3",
                    "enb_ip": "10.0.1.2",
                    "teid_uplink": "0x00490003",
                    "epc_ip": "10.244.1.3",
                    "teid_downlink": "0x00000003"
                },
                "10.10.0.2": {
                    "ue_ip": "10.10.0.2",
                    "enb_ip": "10.0.1.2",
                    "teid_uplink": "0x00460003",
                    "epc_ip": "10.244.1.3",
                    "teid_downlink": "0x00000001"
                }
            }

            GET /upf/v1/uemap/10.10.0.2

            {
                "ue_ip": "10.10.0.2",
                "enb_ip": "10.0.1.2",
                "teid_uplink": "0x00460003",
                "epc_ip": "10.244.1.3",
                "teid_downlink": "0x00000001"
            }
            ...
        """

        if ue_ip:
            return self.service.rest__get_uemap(ue_ip)

        return self.service.rest__get_uemap()
