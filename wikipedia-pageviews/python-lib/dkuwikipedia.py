import dateutil.parser, datetime
import requests

def get_daterange(config):
    beg_date_str = f'{config["begin_date"]}T00:00:00Z'
    beg_date = dateutil.parser.parse(beg_date_str)
    end_date_str = f'{config["end_date"]}T00:00:00Z'
    end_date = dateutil.parser.parse(end_date_str)
    return (beg_date, end_date)

def get_projects(config):
    projects = config["projects"].split(",")
    return [x.strip() for x in projects]


def _get_headers():
    return {
        "User-Agent" : "DSS-Plugin-Wikipedia-Pageviews 0.0.1 (contact@dataiku.com)"
    }

def query_top(project, date):
    """Returns the Requests response"""
    return requests.get(
        f'https://wikimedia.org/api/rest_v1/metrics/pageviews/top/{project}/all-access/{date.strftime("%Y")}/{date.strftime("%m")}/{date.strftime("%d")}',
        headers=_get_headers(),
    )

def query_page(project, page, beg_date, end_date):
    """Returns the Requests response"""
    return requests.get(
        f'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{project}/all-access/all-agents/{page}/daily/{beg_date.strftime("%Y%m%d")}/{end_date.strftime("%Y%m%d")}',
        headers=_get_headers(),
    )

def format_date(date):
    return date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def parse_yyyymmddhh(the_str):
    return datetime.datetime.strptime(the_str, "%Y%m%d%H")

def parse_and_format_yyyymmddhh(the_str):
    return format_date(parse_yyyymmddhh(the_str))