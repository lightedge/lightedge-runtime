#!/usr/bin/env python3
#
# Copyright (c) 2020 Giovanni Baggio
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

"""App manager."""

from pathlib import Path
import json
import shutil
import yaml
from jsonpath_ng import parse as jsonpath_parse

from helmpythonclient.client import HelmPythonClient

from empower_core.service import EService
from empower_core.launcher import srv

from lightedge.managers.appmanager.apphandler import AppHandler
from lightedge.managers.appmanager.repohandler import RepoHandler
from lightedge.managers.appmanager.chartfinderhandler import ChartFinderHandler
from lightedge.managers.appmanager.chartinfohandler import ChartInfoHandler

DEFAULT_HELM = "helm"
DEFAULT_KUBECONFIG = ""
DEFAULT_CHARTS_DIR = ""
DEFAULT_TMP_DIR = "/tmp/lightedge"


class AppManager(EService):
    """App manager."""

    HANDLERS = [AppHandler, RepoHandler, ChartFinderHandler, ChartInfoHandler]

    def __init__(self, context, service_id, **params):

        super().__init__(context=context, service_id=service_id, **params)

        self.helm_client = None
        self.servicemanager = srv("servicemanager")

    def start(self):
        """Start app manager manager."""

        super().start()

        helm_args = {"helm": self.helm, "kubeconfig": self.kubeconfig,
                     "raise_ex_on_err": True}
        self.helm_client = HelmPythonClient(**helm_args)
        version, err = self.helm_client.version(raise_ex_on_err=False)
        if err:
            self.log.error("Exception while using Helm binary: %s", err)
        else:
            self.log.info("Helm version: %s", version.replace("\n", ""))

    def list_apps(self, ns_name):
        """Return the list of all the apps in a namespace."""

        return self.helm_client.list(namespace=ns_name)

    def get_app(self, app_name, ns_name):
        """Return the details of an app."""

        status, _ = self.helm_client.status(app_name, namespace=ns_name)
        values, _ = self.helm_client.get_values(app_name, namespace=ns_name)
        release_data = {"status": status, "values": values}

        schema_path = Path("%s/%s/values.schema.json"
                           % (self._get_ns_dir(ns_name), app_name))
        if schema_path.exists():
            schema = json.loads(schema_path.read_text())
            release_data["schema"] = schema

        return release_data

    def create_app(self, app_name, repochart_name, ns_name, values, **kwargs):
        """Create a new app."""

        app_dir = None
        try:
            if '/' in app_name:
                raise ValueError("no '/' are allowed in the app name")
            if repochart_name.count("/") != 1:
                raise ValueError("Charts must come from a repo (repo/chart)")

            namespace_dir = self._add_ns(ns_name)  # no effect if already there
            app_dir = self._unpack_chart(repochart_name, app_name,
                                         namespace_dir)

            self._write_values(app_name, namespace_dir, values)

            srv_endpoints = kwargs.get("srv_endpoints", None)
            if self.servicemanager and srv_endpoints:
                values = self._get_values(app_name, namespace_dir)
                new_values = self._values_from_endpoints(values, srv_endpoints)
                self._write_values(app_name, namespace_dir, new_values)

            data, _ = self.helm_client.install(app_name, app_name,
                                               chart_dir=namespace_dir,
                                               namespace=ns_name,
                                               create_namespace=True)
            return data

        except Exception as ex:
            if app_dir and app_dir.is_dir():
                shutil.rmtree(app_dir)
            self._delete_ns(ns_name)  # no effect if there are apps inside
            raise ValueError(ex)

    def update_app(self, app_name, ns_name, values):
        """Update an app."""

        namespace_dir = self._get_ns_dir(ns_name)
        self._write_values(app_name, namespace_dir, values)
        self.helm_client.install(app_name, app_name, upgrade=True,
                                 chart_dir=namespace_dir, namespace=ns_name)

    def delete_app(self, app_name, ns_name):
        """Delete an app."""

        release_dir = "%s/%s" % (self._get_ns_dir(ns_name), app_name)
        if not Path(release_dir).is_dir():
            raise ValueError("%s is not a directory" % release_dir)

        shutil.rmtree(release_dir)
        self.helm_client.uninstall(app_name, namespace=ns_name)
        self._delete_ns(ns_name)

    def _unpack_chart(self, repochart_name, app_name, namespace_dir):
        """Download and open a chart."""

        shutil.rmtree(self.tmp_dir, ignore_errors=True)

        chart_name = repochart_name.split("/")[1]

        self.helm_client.pull(repochart_name, chart_dir=self.tmp_dir)

        chart_dir = Path("%s/%s" % (self.tmp_dir, chart_name))
        app_dir = Path("%s/%s" % (namespace_dir, app_name))
        if app_dir.exists():
            raise ValueError("An app with the same name already exist "
                             "in the current namespace")
        shutil.move(chart_dir, app_dir)

        return app_dir

    def _values_from_endpoints(self, values, srv_endpoints):
        """Retrieve updated values from a list of endpoints."""

        new_values = values

        for srv_endpoint in srv_endpoints:

            jsonpath = srv_endpoint["jsonpath"]
            parser = jsonpath_parse(jsonpath)
            jp_data = dict()
            for match in parser.find(values):
                jp_data[str(match.full_path)] = match.value

            service_name = srv_endpoint["name"]
            timeout = None
            if "timeout" in srv_endpoint:
                timeout = srv_endpoint["timeout"]

            new_jp_data = self.servicemanager.send_request(service_name,
                                                           jp_data, timeout)
            parser.update(new_values, list(new_jp_data.values())[0])

        return new_values

    def _get_values(self, app_name, chart_dir):
        """Retrieve the values from the chart."""

        raw, _ = self.helm_client.show_info(app_name, "values",
                                            chart_dir=chart_dir)
        return yaml.load(raw, yaml.SafeLoader)

    def _write_values(self, app_name, chart_dir, values):
        """Write values to a chart."""

        data = self._get_values(app_name, chart_dir)
        new_data = {**data, **values}
        new_raw = yaml.dump(new_data)

        values_path = "%s/%s/values.yaml" % (chart_dir, app_name)
        with open(values_path, mode="w") as values_file:
            values_file.write(new_raw)

    def repo_list(self):
        """Return the list of all configured repositories."""

        data, _ = self.helm_client.repo_list()
        return data

    def repo_add(self, name, url, **kwargs):
        """Add a new repository."""

        self.helm_client.repo_add(name, url, **kwargs)

    def repo_update(self):
        """Update a repository."""

        self.helm_client.repo_update()

    def repo_remove(self, name):
        """Remove a repository."""

        self.helm_client.repo_remove(name)

    def chart_finder(self, keyword):
        """Find a chart from a keyword."""

        data, _ = self.helm_client.search(keyword)
        return data

    def chart_get_info(self, chart_name):
        """Get detailed info about a chart."""

        shutil.rmtree(self.tmp_dir, ignore_errors=True)

        infos = {}
        for field in ("chart", "readme"):
            data, _ = self.helm_client.show_info(chart_name, field)
            infos[field] = data

        self.helm_client.pull(chart_name, chart_dir=self.tmp_dir)
        schema_path = "%s/%s/values.schema.json" \
                      % (self.tmp_dir, chart_name.split("/")[1])
        if Path(schema_path).is_file():
            with open(schema_path, mode="r") as file:
                infos["schema"] = json.loads(file.read())

        return infos

    def _get_ns_dir(self, name=None):
        """Return the directory of a chart from its name."""

        namespaces = dict()
        for folder in Path(self.charts_dir).iterdir():
            if folder.is_dir():
                if name and folder.name == name:
                    return folder
                namespaces[folder.name] = folder
        if namespaces:
            return namespaces
        return None

    def _add_ns(self, ns_name):
        """Add a new namespace folder if it does not already exist."""

        namespace_dir = "%s/%s" % (self.charts_dir, ns_name)
        Path(namespace_dir).mkdir(exist_ok=True)
        return namespace_dir

    def _delete_ns(self, ns_name):
        """Delete a namespace folder if there are no apps inside."""

        ns_dir = self._get_ns_dir(ns_name)
        if ns_dir:
            if sum(1 for app_dirs in ns_dir.iterdir()) == 0:
                shutil.rmtree(ns_dir)

    @property
    def helm(self):
        """Return helm."""

        return self.params["helm"]

    @helm.setter
    def helm(self, value):
        """Set helm."""

        self.params["helm"] = value

    @property
    def kubeconfig(self):
        """Return kubeconfig."""

        return self.params["kubeconfig"]

    @kubeconfig.setter
    def kubeconfig(self, value):
        """Set kubeconfig."""

        self.params["kubeconfig"] = value

    @property
    def charts_dir(self):
        """Return charts_dir."""

        return self.params["charts_dir"]

    @charts_dir.setter
    def charts_dir(self, value):
        """Set charts_dir."""

        self.params["charts_dir"] = value

    @property
    def tmp_dir(self):
        """Return tmp_dir."""

        return self.params["tmp_dir"]

    @tmp_dir.setter
    def tmp_dir(self, value):
        """Set tmp_dir."""

        self.params["tmp_dir"] = value


def launch(context, service_id, **kwargs):
    """ Initialize the module. """

    return AppManager(context=context, service_id=service_id,
                      helm=kwargs.get("helm", DEFAULT_HELM),
                      kubeconfig=kwargs.get("kubeconfig", DEFAULT_KUBECONFIG),
                      charts_dir=kwargs.get("charts_dir", DEFAULT_CHARTS_DIR),
                      tmp_dir=kwargs.get("tmp_dir", DEFAULT_TMP_DIR))
