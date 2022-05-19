import dataiku
def do(payload, config, plugin_config, inputs):
    """
    Create list of options of projects in instance.
    """
    projects = dataiku.api_client().list_projects()
    choices = [
        {
            "value": project.get('projectKey'),
            "label": project.get('projectKey'),
        }
        for project in projects
    ]

    return {"choices": choices}