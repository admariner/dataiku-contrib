from dataiku.connector import Connector
import sys
from bs4 import UnicodeDammit
import logging

logger = logging.getLogger(__name__)


if (sys.version_info > (3, 0)):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen



class GutenbergConnector(Connector):

    def __init__(self, config):
        """
        The configuration parameters set up by the user in the settings tab of the
        dataset are passed as a json object 'config' to the constructor
        """
        Connector.__init__(self, config)  # pass the parameters to the base class

        # Fetch configuration
        self.mirror = self.config['mirror']
        self.book_id= self.config['book_id']

    def get_read_schema(self):
        """
        Returns the schema for the Gutenberg connector.
        """

        # The Gutenberg connector does not specify a schema,
        # so DSS will infer the schema
        # from the columns actually returned by the generate_rows method
        return None


    def generate_rows(self, dataset_schema=None, dataset_partitioning=None,
                            partition_id=None, records_limit = -1):
        """
        The main reading method.
        """

        url_book = self.mirror
        lid = len(str(self.book_id))
        fullbid = str(self.book_id)
        rootbid = fullbid # sometimes the id to access a file has a variation, ex fullbid=14285-8 for the book 14285

        stopit = 0
        for i in range(lid-1):
            if (fullbid[i+1] != "-") and (stopit==0):
                url_book += f'/{fullbid[i]}'
            else:
                stopit=1
                rootbid = fullbid[:i]
        url_book += f'/{rootbid}/{fullbid}-0.txt'

        response = urlopen(url_book)
        raw = response.read()   #.decode('utf8')
        converted = UnicodeDammit(raw)
        raw = converted.unicode_markup
        start_book = raw.find("START OF")
        end_book = raw.rfind('END OF')
        preamb = raw[:start_book]

        author = [ i.split(':')[1].strip() for i in preamb.split("\r\n\r\n") if i.find('Author') != -1][0]
        title = [ i.split(':')[1].strip() for i in preamb.split("\r\n\r\n") if i.find('Title') != -1][0]
        date = [ i.split(':')[1].strip() for i in preamb.split("\r\n\r\n") if i.find('Release Date') != -1][0]
        book_paraph =  raw[start_book:end_book].split("\r\n\r\n")

        logger.info(f"Book length {len(raw)}")
        logger.info("N paragraphs:", len(book_paraph))

        for id_p, p in enumerate(book_paraph):
            yield {'id':id_p, 'author': author, 'title': title, 'text': p}
