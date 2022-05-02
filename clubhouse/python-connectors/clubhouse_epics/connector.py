from dataiku.connector import Connector
import datetime
import json
import logging
from utils import byteify
import requests

class EpicsConnector(Connector):

    def __init__(self, config, plugin_config):
        Connector.__init__(self, config, plugin_config)  # pass the parameters to the base class
        self.endpoint = "https://api.clubhouse.io/api/beta"
        self.key = plugin_config["api_token"]

    def list_epics(self):
        logging.info("Clubhouse: fetching epics")
        headers = {"Content-Type": "application/json"}

        r = requests.get(self.endpoint + "/epics?token=" + self.key, headers=headers)
        r.raise_for_status()
        try:
            return json.loads(r.content)
        except Exception:
            logging.info("Could not parse json from request content:\n" + r.content)
            raise

    def get_read_schema(self):
        # Let DSS infer the schema from the columns returned by the generate_rows method
        return None

    def generate_rows(self, dataset_schema=None, dataset_partitioning=None,
                      partition_id=None, records_limit = -1):
        query_date = datetime.datetime.now()

        rows = self.list_epics()
        if len(rows) == 0:
            logging.info("Not epics.")
        else:
            nb = 0
            for row in rows:
                if 0 <= records_limit <= nb:
                    logging.info("Reached records_limit (%i), stopping." % records_limit)
                    return

                encoded_row = {}
                encoded_row["query_date"] = query_date
                for key in row:
                    encoded_row[str(key)] = byteify(row[key])

                yield encoded_row
                nb += 1

