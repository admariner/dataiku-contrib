from dataiku.runnables import Runnable, ResultTable
import dataiku
import subprocess
import os, os.path as osp
import cleanup

class MyRunnable(Runnable):
    def __init__(self, project_key, config, plugin_config):
        self.project_key = project_key
        self.config = config
        
    def get_progress_target(self):
        return (100, 'NONE')

    def run(self, progress_callback):
        dip_home = os.environ['DIP_HOME']
        saved_models = osp.join(dip_home, 'saved_models')

        rt = ResultTable()
        rt.set_name("Analysis data used space")
        rt.add_column("project", "Project key", "STRING")
        rt.add_column("saved_model_id", "Saved model id", "STRING")
        rt.add_column("saved_model_name", "Saved model name", "STRING")
        rt.add_column("total", "Total space (MB)", "STRING")
        rt.add_column("splits", "Splits space (MB)", "STRING")
        rt.add_column("versions", "Number of versions", "STRING")

        if self.config.get('allProjects', False):
            projects = list(os.listdir(saved_models))
        else:
            projects = [self.project_key]

        for project in projects:
            project_sm = osp.join(saved_models, project)

            if not osp.isdir(project_sm):
                continue

            for saved_model in os.listdir(project_sm):
                sm_dir = osp.join(project_sm, saved_model)
                versions_dir = osp.join(sm_dir, "versions")

                if not osp.isdir(versions_dir):
                    continue

                versions = 0
                total_splits = 0
                total = cleanup.du(sm_dir)

                for version in os.listdir(versions_dir):
                    version_dir = osp.join(versions_dir, version)
                    split_dir = osp.join(version_dir, "split")
                    if osp.isdir(split_dir):
                        total_splits += cleanup.du(split_dir)
                    versions += 1

                record = [
                    project,
                    saved_model,
                    saved_model,
                    total / 1024,
                    total_splits / 1024,
                    versions,
                ]

                rt.add_record(record)

        return rt