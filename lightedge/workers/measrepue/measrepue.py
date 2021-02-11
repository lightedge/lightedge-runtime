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

"""Measurement Report UE Subscription."""

import uuid

from empower_core.app import EVERY
from empower_core.plmnid import PLMNID
from empower_core.imsi import IMSI

from lightedge.managers.rnismanager.subscription import Subscription


class MeasRepUe(Subscription):
    """Meas Rep UE."""

    SUB_TYPE = "meas_rep_ue"
    SUB_CONFIG = "MeasRepUeSubscription"
    SUB_PARAMS = ['callbackReference', 'expiryDeadline',
                  'filterCriteriaAssocTri', 'subscriptionType']

    def __init__(self, context, service_id, every, subscription):

        super().__init__(context=context, service_id=service_id, every=every,
                         subscription=subscription)

        self.app_id = None

    def find_project_id(self, ):
        """Find project id from PLMN."""

        plmn = self.subscription['filterCriteriaAssocTri']['ecgi']['plmn']
        plmnid = PLMNID("".join(plmn.values()))

        req = self.manager.get("/projects")

        if not req.status_code == 200:
            self.log.error("Unable to find PLMN %s", plmnid)
            return None

        project_id = None

        for project in req.json().values():

            if not project['lte_props']:
                continue

            current = PLMNID(project['lte_props']['plmnid'])

            if current == plmnid:
                project_id = uuid.UUID(project['project_id'])
                break

        url = "/projects/%s" % project_id
        req = self.manager.get(url)

        if req.status_code != 200:
            self.log.error("Unable to find PLMN %s", plmnid)
            return None

        return project_id

    def loop(self):
        """Periodic loop."""

        project_id = self.find_project_id()

        if not project_id:
            return

        url = "/projects/%s/apps/%s" % (project_id, self.app_id)
        req = self.manager.get(url)

        if req.status_code != 200:
            self.create_worker(project_id)

        self.create_callback(project_id)

    def create_worker(self, project_id):
        """Create new worker on empower."""

        associate_id = \
            self.subscription['filterCriteriaAssocTri']['associateId'][0]

        if associate_id['type'] != 'IMSI':
            return

        imsi = IMSI(associate_id['value'])

        data = {
            "name": "empower.apps.uemeasurements.uemeasurements",
            "params": {
                "imsi": imsi.to_str(),
                "meas_id": 1,
                "interval": "MS240",
                "amount": "INFINITY"
            }
        }

        req = self.manager.post("/projects/%s/apps" % project_id, data)

        if not req.status_code == 201:
            self.log.error("Unable to create worker, error %u",
                           req.status_code)
            return

        location = req.headers['Location']

        self.app_id = location.split("/")[-1]

    def create_callback(self, project_id):
        """Create new callback."""

        callback = "http://127.0.0.1:8889/rni/v2/subscriptions/%s/ch" % \
            self.service_id

        data = {
            "version": "1.0",
            "name": "default",
            "callback": callback,
            "callback_type": "rest"
        }

        url = "/projects/%s/apps/%s/callbacks" % (project_id, self.app_id)
        req = self.manager.post(url, data)

        if not req.status_code == 201:
            self.log.error("Unable to create callback, error %u",
                           req.status_code)
            return


def launch(context, service_id, subscription, every=EVERY):
    """ Initialize the module. """

    return MeasRepUe(context=context, service_id=service_id, every=every,
                     subscription=subscription)
