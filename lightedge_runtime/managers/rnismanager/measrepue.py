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

from empower_core.serialize import serializable_dict


@serializable_dict
class MeasRepUe:
    """Meas Rep UE."""

    def __init__(self, subscription_id, callbackReference, filterCriteria,
                 expiryDeadline):

        self.subscription_id = subscription_id
        self.callback_reference = callbackReference
        self.filter_criteria = filterCriteria
        self.expiry_deadline = expiryDeadline

    def to_dict(self):
        """Return a dict representation of the object."""

        out = {
            "subscription_id": self.subscription_id,
            "callback_reference": self.callback_reference,
            "filter_criteria": self.filter_criteria,
            "expiry_deadline": self.expiry_deadline
        }

        return out
