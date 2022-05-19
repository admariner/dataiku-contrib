import time
import os.path
import datetime
import dataiku
import dataikuapi
from dataiku.runnables import Runnable
from dataikuapi.utils import DataikuException


class MyRunnable(Runnable):

    def __init__(self, project_key, config, plugin_config):
        """
        :param project_key: the project in which the runnable executes
        :param config: the dict of the configuration of the object
        :param plugin_config: contains the plugin settings
        """
        self.project_key = project_key
        self.config = config
        self.plugin_config = plugin_config
        
    def get_progress_target(self):
        return None

    def run(self, progress_callback):
        
        # verify inputs
        bundle_id = self.config.get("bundle_id", "")
        if bundle_id == "":
            raise Exception("bundle_id is required")

        remote_host = self.config.get("remote_host", "")
        if remote_host == "":
            raise Exception("destination is required")

        api_key = self.config.get("api_key", "")
        if api_key == "":
            raise Exception("API key is required")

        activate_scenarios = self.config.get("activate_scenarios")

        if ignore_proxy_conf := self.config.get("ignore_proxy_env_settings"):
            os.environ.pop('http_proxy', None)
            os.environ.pop('https_proxy', None)

        # get client and connect to project
        client = dataiku.api_client()
        project = client.get_project(self.project_key)

        # use public python api to get access to remote host
        remote_client = dataikuapi.DSSClient(remote_host, api_key)

        # ignore SSL Certificates if selected
        if self.config.get("ignore_ssl_certs"):
            remote_client._session.verify = False

        html = f'<div> Successfully connected to remote host: {remote_client.host}</div>'


        # get list of connections used in the initial project
        datasets = project.list_datasets()
        connections_used = []

        for dataset in datasets:
            try:
                connections_used.append(dataset['params']['connection'])
            except:
                continue

        connections_used = list(set(connections_used))

        # get list of connections in remote project
        remote_connections_list = remote_client.list_connections()
        remote_connections_names = remote_connections_list.keys()

        # check if connections used in the initial project also exist on the remote instance
        for connection in connections_used:
            if connection in remote_connections_names:
                continue

            error_msg = f'Failed - Connection {connection} used in initial project does not exist on instance {remote_host}.'

            raise Exception(error_msg)

        html += '<div><div>All connections exist on both instances</div>'

        # check if any plugins installed in the original instance are not installed in remote instance
        # get list of plugins in original instance
        original_plugin_names = {
            plugin['meta']['label']: plugin['version']
            for plugin in client.list_plugins()
        }

        # compare to list of plugins in remote instance
        remote_plugin_names = {
            plugin['meta']['label']: plugin['version']
            for plugin in remote_client.list_plugins()
        }

        missing_plugins = {k: original_plugin_names[k] for k in original_plugin_names if k not in remote_plugin_names or original_plugin_names[k] == remote_plugin_names[k]}

        if missing_plugins:
            html += '<div> <b> Warning: the following plugins (and versions) are installed on this instance, but not on the remote instance. Please ensure that your project does not use these plugins before proceeding. </b> </div>'
            html += '<table>'
            html += '<tr>'
            html += '<th>Plugin</th>'
            html += '<th>Version</th>'
            html += '</tr>'

        for plugin, value in missing_plugins.items():
            html += '<tr>'
            html += f'<td> {plugin} </td>'
            html += f'<td> {value} </td>'
            html += '</tr>'

        if missing_plugins:
            html += '</table>'

        ''' TRIGGER THE BELOW SCENARIO CODE IF CHECKBOX CHECKED '''
        # get a list of active scenario ids on the project
        if activate_scenarios:
            project_active_scenarios = []

            for scenario in project.list_scenarios():
                s = project.get_scenario(scenario['id'])
                scenario_def = s.get_definition()
                if scenario_def['active']:
                    project_active_scenarios.append(scenario_def['id'])

        # create the bundle (verify that the bundle_id does not exist)
        try:
            project.export_bundle(bundle_id)
            html += f'<div><div>Successfully created bundle: {bundle_id}</div>'
        except DataikuException as de:
            error_msg = f'Failed - Bundle {bundle_id} already exists for project {self.project_key}'

            raise Exception(error_msg)

        # check if there are any projects in remote instance
        try:
            remote_projects = remote_client.list_project_keys()
        except:
            remote_projects = []

        # if the project doesnt exist, create it. Otherwise update with the new bundle
        with project.get_exported_bundle_archive_stream(bundle_id) as fp:
            if self.project_key not in remote_projects:
                remote_client.create_project_from_bundle_archive(fp.content)

            else:
                remote_project = remote_client.get_project(self.project_key)
                remote_project.import_bundle_from_stream(fp.content)

        # connect to remote project
        remote_project = remote_client.get_project(self.project_key)

        # "preload bundle" to create/update custom code environments used throughout the project
        preload = remote_project.preload_bundle(bundle_id)

        # activate bundle
        remote_project.activate_bundle(bundle_id)
        html += '<div> Bundle activated </div>'

        ''' TRIGGER THE BELOW SCENARIO CODE IF CHECKBOX CHECKED '''
        # activate scenarios that were active on design instance
        if activate_scenarios:
            for active_scenario_id in project_active_scenarios:
                scenario = remote_project.get_scenario(active_scenario_id)
                scenario_def = scenario.get_definition()
                scenario_def['active'] = True
                scenario.set_definition(scenario_def)

        if remote_design_instance := self.config.get("remote_design_instance"):
            if create_bundle_on_remote_design_instance := self.config.get(
                "create_bundle_on_remote_design_instance"
            ):
                remote_project.export_bundle(bundle_id)
                html += '<div> Bundle Created on Remote Design Instance </div>'

        html += '</div>'
        return html
    
    
    
    
