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

# import lightedge_runtime.managers.apimanager.apimanager as apimanager
import empower_core.apimanager.apimanager as apimanager


# pylint: disable=W0223
class MatchMapHandler(apimanager.APIHandler):
    """All the accounts defined in the controller."""

    URLS = [r"/upf/v1/matchmap/([-0-9.]*)",
            r"/upf/v1/matchmap/(\bchecked\b)",
            r"/upf/v1/matchmap"]

    @apimanager.validate(min_args=0, max_args=1)
    def get(self, match_index=0):
        """List entries in the Match Map.

        Args:

            [0]: the Match Index

        Example URLs:

            GET /upf/v1/matchmap

            [
                {
                    "ip_proto_num": "1",
                    "dst_ip": "31.13.0.0",
                    "dst_port": "0",
                    "netmask": "16",
                    "new_dst_ip": null,
                    "new_dst_port": 0
                },
                {
                    "ip_proto_num": "1",
                    "dst_ip": "2.2.2.2",
                    "dst_port": "0",
                    "netmask": "32",
                    "new_dst_ip": "192.168.0.1",
                    "new_dst_port": 0
                },
                {
                    "ip_proto_num": "0",
                    "dst_ip": "31.13.0.0",
                    "dst_port": "0",
                    "netmask": "16",
                    "new_dst_ip": "127.0.0.1",
                    "new_dst_port": 0
                },
                {
                    "ip_proto_num": "6",
                    "dst_ip": "18.185.97.149",
                    "dst_port": "0",
                    "netmask": "32",
                    "new_dst_ip": "10.104.0.26",
                    "new_dst_port": 0
                }
            ]

            GET /upf/v1/matchmap/2

            {
                "ip_proto_num": "1",
                "dst_ip": "2.2.2.2",
                "dst_port": "0",
                "netmask": "32",
                "new_dst_ip": "192.168.0.1",
                "new_dst_port": 0
            }

        """
        
        # self.service.upf_request_validator.get_matchmap(match_index)

        # if match_index:
        #     return self.service.matches[int(match_index) - 1]

        # return self.service.matches

        if match_index == '':
            match_index = 0
        if match_index == 'checked':
            return self.service.rest__get_matchmap_checked()

        return self.service.rest__get_matchmap(int(match_index) - 1)

    @apimanager.validate(returncode=201, min_args=0, max_args=1)
    def post(self, match_index=1, **request_data):
        """Insert entry in the Match Map.

        Args:

            [0]: the Match Index

        Request:
            version: protocol version (1.0)
            params: the list of parameters to be set

        Example URLs:

            POST /upf/v1/matchmap
            POST /upf/v1/matchmap/5

            {
                "ip_proto_num": 6,
                "dst_ip":
                    "ec2-18-185-97-149.eu-central-1.compute.amazonaws.com",
                "netmask": 32,
                "dst_port": 0,
                "new_dst_ip": "nginx-service",
                "new_dst_port": 0
            }

            ...
        """
        # if match_index:
        #     match_index = int (match_index)
        #     if match_index <= 0:
        #         message = "Invalid match index '%i': must be greater than 0"\
        #                   % match_index 
        #         raise ValueError(message)
        #     matches_length = len(self.service.matches)
        #     if matches_length == 0:
        #         if match_index != 1:
        #             message =\
        #                 "Match list is void: inserting match index has to be 1"\
        #                 % match_index 
        #             raise ValueError(message)
        #     elif match_index > matches_length:
        #         message = "Invalid match index '%i': acceptable range is [1, %i]"\
        #                   % (match_index, matches_length )
        #         raise ValueError(message)
        #     return self.service.matches[int(match_index) - 1]

        # self.service.upf_request_validator.post_matchmap(match_index, 
        #                                                  request_data)

        if match_index == '':
            match_index = 1

        self.service.rest__add_matchmap(int(match_index) - 1, request_data)

        self.set_header("Location", "/upf/v1/matchmap/%s" % match_index)
        self.set_status(201)

    @apimanager.validate(returncode=204, min_args=0, max_args=1)
    def delete(self, match_index=0):
        """Delete entries in the Match Map.

        Args:

            [0]: the Match Index

        Example URLs:

            DELETE /upf/v1/matchmap
            DELETE /upf/v1/matchmap/5

        """

        if match_index == '':
            match_index = 0

        # no match in url -> match_index < 0 -> remove all
        self.service.rest__del_matchmap(int(match_index) - 1)
