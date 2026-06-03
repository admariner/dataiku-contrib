# Wikipedia page views plugin

## Summary

This plugin lets you retrieve Wikipedia page view statistics from the Wikimedia Pageviews API.

It provides:

- a connector to retrieve the top viewed pages per day for one or more Wikipedia projects
- a connector to retrieve the page views of selected pages over time
- a recipe to retrieve the page views of selected pages over time from an input dataset

## Components

### Connector: Top pageviews per day

This connector returns the top viewed pages per day for one or more Wikipedia projects.

Parameters:

- **Wikipedia projects**: comma-separated list such as `en.wikipedia, fr.wikipedia`
- **Begin date**
- **End date**

Dates must be provided in `YYYYMMDD` format.

### Connector: Pageviews of selected pages over time

This connector returns the page views of selected pages over time.

Parameters:

- **Pages to follow**: one page per line, in the form `project page`, for example `en.wikipedia Dataiku`
- **Begin date**
- **End date**

Dates must be provided in `YYYYMMDD` format.

### Recipe: Pageviews of selected pages over time

This recipe expects an input dataset with at least two columns:

- `project`
- `page`

For each `(project, page)` pair, the recipe queries the Wikimedia API and writes an output dataset with the following columns:

- `project`
- `page`
- `date`
- `views`

## License

This plugin is distributed under the Apache Software License.
