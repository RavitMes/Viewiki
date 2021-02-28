import re
import numpy as np
import pandas as pd
from collections import defaultdict
from urllib.parse import unquote
import logging


class DataPreprocessing:
    def __init__(self, df):
        self.logger = logging.getLogger(__name__)
        self.df = df

    def translate_url(self, url):
        self.logger.info(f"translate the url {url}")
        try:
            return unquote(url)
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")
            return url

    def preprocessing(self):
        try:
            self.logger.info("data preprocessing")
            self.df.reset_index(inplace=True)
            self.df.to_csv("check_df.csv")
            self.df['wiki_page_only'] = self.df["WIKI_PAGE_URL"].apply(
                lambda x: self.translate_url(self.extract_original_link(x)))
            self.df["page_interlink_only"] = self.df["PAGE_INTERLINK"].apply(
                lambda x: self.translate_url(self.extract_original_link(x)))
            list_links = list(self.df.wiki_page_only) + list(self.df.page_interlink_only)
            d_links = dict(enumerate(list(set(list_links))))
            d_links = {k:v for k,v in d_links.items() if str(v)!="nan"}
            network = self.df[["wiki_page_only", "page_interlink_only"]]
            network.to_csv("wiki_network.csv")
            network_adjusted = network.copy()
            network_adjusted["wiki_page_only"] = network_adjusted["wiki_page_only"].str.replace("_",
                                                                                                "+")
            network_adjusted["page_interlink_only"] = network_adjusted[
                "page_interlink_only"].str.replace("_", "+")
            network_adjusted.to_csv("wiki_network_adjusted.csv")
            d_types = defaultdict()
            categories = list(self.df["CATEGORY"].unique())
            self.logger.info(f"categories are: {categories}")
            for idx, record in self.df.iterrows():
                if record["CATEGORY"]=="Interlink":
                    d_types[record['page_interlink_only']] = 'Interlink'
                else:
                    d_types[record['wiki_page_only']] = record['CATEGORY']

            df_types = pd.DataFrame.from_dict(d_types, orient="index")
            df_types.to_csv("df_types.csv")
            return network, network_adjusted, df_types
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def extract_original_link(self, link):
        self.logger.info(f"extract_original_link for the link {link}")
        try:
            if "#" in link:
                org = re.findall("https://en.wikipedia.org/wiki/(.+)#", link)[0]
            else:
                org = re.findall("https://en.wikipedia.org/wiki/(.+)", link)[0]

            return org
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")
            return np.nan
