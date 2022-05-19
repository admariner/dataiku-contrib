import requests, json
import pandas as pd
from dataiku.connector import Connector
import importio_utils

class ImportIOConnector(Connector):

    def __init__(self, config):
        """Make the only API call, which downloads the data"""
        Connector.__init__(self, config)
        if self.config['api_url'].startswith('https://api.import.io/'):
            self.api_version = 'api'
        elif self.config['api_url'].startswith('https://extraction.import.io/'):
            self.api_version = 'extraction'
        else:
            raise Exception(
                'It looks like this URL is not an API URL. URLs to call the API (and get a json response) start with "https://api.import.io" .')
        print '[import.io connector] calling API...'
        response = requests.get(self.config['api_url'])
        print '[import.io connector] got response'
        try:
            self.json = response.json()
        except Exception as e:
            print e
            print 'response was:\n', response.text
            raise

    def get_read_schema(self):
        if self.api_version != 'api':
            return None
        columns = importio_utils.convert_schema(self.json['outputProperties'])
        return {"columns":columns}

    def generate_rows(self, dataset_schema=None, dataset_partitioning=None, partition_id=None, records_limit = -1):
        if self.api_version == 'api':
            yield from self.json['results']
        else:
            df = pd.DataFrame(self.json['extractorData']['data'][0]['group'])
            for col in df.columns:
                lengths = df[col].apply(lambda x: len(x) if type(x) == list else 0)
                if lengths.max() == 1:
                    df[col] = df[col].apply(lambda x: x[0] if type(x) == list else {})
                    keys = df[col].apply(lambda x: x.keys())
                    for key in {key for line in keys for key in line}: # drop duplicates
                        df[col + '_' + key] = df[col].apply(lambda x: x.get(key,''))
                    del df[col]
                else:
                    df[col] = df[col].apply(json.dumps)
            yield from df.to_dict(orient='records')
