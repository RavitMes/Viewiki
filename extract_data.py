import pandas as pd
import urllib.request, json
from urllib.parse import quote
import logging
import math


class ExtractData:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def define_src_page(self, links):
        """
        recieves links: list with link titles names
        return: string representing the request (for a GET requests)
        """
        try:
            self.logger.info("define_src_page")
            queries = []
            template = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop" \
                       "=pageviews" \
                       "&titles="
            links = [x.replace("+", " ") for x in links]
            i = 0
            titles = links[i]
            while i < len(links)-1:
                i += 1
                if i % 2 == 0:
                    titles = titles.strip("|")
                    source = template + quote(titles)
                    queries.append(source)
                    titles = links[i]
                else:
                    titles += "|"
                    titles += links[i]

            source = template + quote(titles)
            queries.append(source)
            queries = [source.strip('%7C') for source in queries]

            return queries
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def extract_json(self, source):
        """recieve a list of queries for the GET request, creates the request and return the
        resulted data
        in a json file"""
        try:
            self.logger.info("extract json_data from the source path")
            with urllib.request.urlopen(source) as url:
                data = json.loads(url.read().decode())['query']['pages']
            return data
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args} for the source {source}")

    def find_links_from_df(self, network_df):
        """
        recieves a csv file name consisting the columns "wiki_page_only" and
        "page_interlink_only" and creates a list of links
        """
        try:
            self.logger.info("find_links_from_df")
            list_links = list(network_df.wiki_page_only) + list(network_df.page_interlink_only)
            links = [x for x in set(list_links) if str(x) != 'nan']
            return links
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def create_df_from_json(self, data):
        """
        recieves a json data and convert it to a dataframe in a required f
        """
        try:
            self.logger.info("create_df_from_json")
            data_df = pd.DataFrame.from_dict(data).T
            print(data_df)
            data_df.reset_index(inplace=True)
            for k in data_df['pageviews'][0].keys():
                data_df[k] = ""

            for idx, record in data_df.iterrows():
                if type(record['pageviews']) is not dict:
                    self.logger.info(f"the record {record} is not a dict")
                    for k, v in data_df['pageviews'][0].items():
                        record[k] = 0
                else:
                    for k, v in record['pageviews'].items():
                        record[k] = v

            return data_df
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def create_final_df(self, network_df):
        try:
            self.logger.info("create_final_df")
            links = self.find_links_from_df(network_df)
            sources = self.define_src_page(links)
            for i in range(len(sources)):
                data = self.extract_json(sources[i])
                if i == 0:
                    data_df = self.create_df_from_json(data)
                else:
                    new_df = self.create_df_from_json(data)
                    data_df = pd.concat([data_df, new_df])
            return data_df
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def find_dicts(self, data_df):
        try:
            self.logger.info("find_dicts")
            data_df.to_csv("data_df_find_dicts.csv")
            d = data_df[['index', 'title']].set_index("index").to_dict()['title']
            d_opposite = {v: k for k, v in d.items()}
            return d, d_opposite
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def create_views_df(self, data_df):
        try:
            self.logger.info("find_dicts")
            views_df = data_df.set_index("index")
            views_df.to_csv("views_df_before.csv")
            views_df = views_df.iloc[:, 4:]
            views_df.to_csv("views_df_after.csv")
            return views_df
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")
