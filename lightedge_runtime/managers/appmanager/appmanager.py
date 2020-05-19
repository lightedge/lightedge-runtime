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
import yaml
import shutil
from jsonpath_ng import parse as jsonpath_parse

from helmpythonclient.client import HelmPythonClient

from lightedge_runtime.managers.appmanager.apphandler import AppHandler
from lightedge_runtime.managers.appmanager.repohandler import RepoHandler
from lightedge_runtime.managers.appmanager.chartfinderhandler \
    import ChartFinderHandler
from lightedge_runtime.managers.appmanager.chartinfohandler import \
    ChartInfoHandler

from empower_core.service import EService
from empower_core.launcher import srv

DEFAULT_HELM = "helm"
DEFAULT_KUBECONFIG = ""
DEFAULT_CHARTS_DIR = ""
DEFAULT_TMP_DIR = "/tmp/lightedge"


class AppManager(EService):
    """App manager."""

    HANDLERS = [AppHandler, RepoHandler, ChartFinderHandler, ChartInfoHandler]

    def __init__(self, context, service_id, helm, kubeconfig, charts_dir,
                 tmp_dir):

        super().__init__(context=context, service_id=service_id, helm=helm,
                         kubeconfig=kubeconfig, charts_dir=charts_dir,
                         tmp_dir=tmp_dir)

        self.helm_client = None
        self.servicemanager = srv("servicemanager")

    def start(self):
        """Start app manager manager."""

        super().start()

        helm_args = {"helm": self.helm, "kubeconfig": self.kubeconfig,
                     "raise_ex_on_err": True}
        self.helm_client = HelmPythonClient(**helm_args)

    def list_apps(self, ns):

        return self.helm_client.list(namespace=ns)

    def get_app(self, app_name, ns):

        status, _ = self.helm_client.status(app_name, namespace=ns)
        values, _ = self.helm_client.get_values(app_name, namespace=ns)
        release_data = {"status": status, "values": values}

        schema_path = Path("%s/%s/values.schema.json"
                           % (self.get_ns_dir(ns), app_name))
        if schema_path.exists():
            schema = json.loads(schema_path.read_text())
            release_data["schema"] = schema

        return release_data

    def create_app(self, app_name, repochart_name, ns, values, srv_endpoints):

        app_dir = None
        try:
            if '/' in app_name:
                raise ValueError("no '/' are allowed in the app name")
            if repochart_name.count("/") != 1:
                raise ValueError("Charts must come from a repo (repo/chart)")

            namespace_dir = self.add_ns(ns)  # no effect if it already exists
            app_dir = self.unpack_chart(repochart_name, app_name,
                                        namespace_dir)

            self.write_values(app_name, namespace_dir, values)

            if self.servicemanager:
                values = self.get_values(app_name, namespace_dir)
                new_values = self.values_from_endpoints(values, srv_endpoints)
                self.write_values(app_name, namespace_dir, new_values)

            data, _ = self.helm_client.install(app_name, app_name,
                                               chart_dir=namespace_dir,
                                               namespace=ns)
            return data

        except Exception as ex:
            if app_dir and app_dir.is_dir():
                shutil.rmtree(app_dir)
            self.delete_ns(ns)  # no effect if there are apps inside
            raise ValueError(ex)

    def update_app(self, app_name, ns, values):

        namespace_dir = self.get_ns_dir(ns)
        self.write_values(app_name, namespace_dir, values)
        self.helm_client.install(app_name, app_name, upgrade=True,
                                 chart_dir=namespace_dir, namespace=ns)

    def delete_app(self, app_name, ns):

        release_dir = "%s/%s" % (self.get_ns_dir(ns), app_name)
        if not Path(release_dir).is_dir():
            raise ValueError("%s is not a directory" % release_dir)

        shutil.rmtree(release_dir)
        self.helm_client.uninstall(app_name, namespace=ns)
        self.delete_ns(ns)

    def unpack_chart(self, repochart_name, app_name, namespace_dir):

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

    def values_from_endpoints(self, values, srv_endpoints):

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

    def get_values(self, app_name, chart_dir):

        raw, _ = self.helm_client.show_info(app_name, "values",
                                            chart_dir=chart_dir)
        return yaml.load(raw, yaml.SafeLoader)

    def write_values(self, app_name, chart_dir, values):

        data = self.get_values(app_name, chart_dir)
        new_data = {**data, **values}
        new_raw = yaml.dump(new_data)

        with open("%s/%s/values.yaml" % (chart_dir, app_name), mode="w") as f:
            f.write(new_raw)

    def repo_list(self):

        data, _ = self.helm_client.repo_list()
        return data

    def repo_add(self, name, url, **kwargs):

        data, _ = self.helm_client.repo_add(name, url, **kwargs)

    def repo_update(self):

        data, _ = self.helm_client.repo_update()

    def repo_remove(self, name):

        data, _ = self.helm_client.repo_remove(name)

    def chart_finder(self, keyword):

        data, _ = self.helm_client.search(keyword)
        return data

    def chart_get_info(self, chart_name):

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

    def get_ns_dir(self, name=None):

        namespaces = dict()
        for folder in Path(self.charts_dir).iterdir():
            if folder.is_dir():
                if name and folder.name == name:
                    return folder
                else:
                    namespaces[folder.name] = folder
        if namespaces:
            return namespaces
        else:
            return None

    def add_ns(self, ns):
        namespace_dir = "%s/%s" % (self.charts_dir, ns)
        Path(namespace_dir).mkdir(exist_ok=True)
        return namespace_dir

    def delete_ns(self, ns):
        ns_dir = self.get_ns_dir(ns)
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


def launch(context, service_id, helm=DEFAULT_HELM,
           kubeconfig=DEFAULT_KUBECONFIG,
           charts_dir=DEFAULT_CHARTS_DIR, tmp_dir=DEFAULT_TMP_DIR):
    """ Initialize the module. """

    return AppManager(context=context, service_id=service_id, helm=helm,
                      kubeconfig=kubeconfig, charts_dir=charts_dir,
                      tmp_dir=tmp_dir)
