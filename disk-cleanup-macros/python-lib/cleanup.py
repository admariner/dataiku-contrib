import subprocess, os, os.path as osp
def du(directory, size_unit="k"):
    """disk usage in kilobytes"""
    return int(
        subprocess.check_output(['du', f'-s{size_unit}', directory])
        .split()[0]
        .decode('utf-8')
    )

def get_projects_to_consider(current_project_key, config):
    mode =  config.get('projectsMode', "CURRENT")

    if mode == "ALL_BUT_IGNORED":
        dip_home = os.environ["DIP_HOME"]
        config_projects = osp.join(dip_home, "config", "projects")
        all_projects = set(os.listdir(config_projects))
        ignored = {x.strip() for x in config.get("ignoredProjects", "").split(",")}
        projects = list(all_projects - ignored)
    elif mode == "INCLUDED":
        projects = list(
            {x.strip() for x in config.get("includedProjects", "").split(",")}
        )

    elif mode == "CURRENT":
        projects = [current_project_key]
    else:
        raise Exception(f"Unexpected projects mode: {mode}")

    return projects

def format_size(size):
    if size is None:
        return 'N/A'
    elif size < 1024:
        return f'{size} b'
    elif size < 1024 * 1024:
        return f'{int(size/1024)} Kb'
    elif size < 1024 * 1024 * 1024:
        return f'{int(size/(1024*1024))} Mb'
    else:
        return f'{int(size/(1024*1024*1024))} Gb'
