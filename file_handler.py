from data_preprocessing import DataPreprocessing
from extract_data import ExtractData
import logging


class FileHandler:
    def __init__(self, df_data):
        self.df_data = df_data
        self.network = None
        self.network_adjusted = None
        self.df_types = None
        self.data_df = None
        self.d_id_title = None
        self.d_title_id = None
        self.views_df = None
        self.extract_data = ExtractData()
        self.logger = logging.getLogger(__name__)

    def organize_data(self):
        self.logger.info("organize data")
        try:
            data_preprocessing = DataPreprocessing(self.df_data)
            network, network_adjusted, df_types = data_preprocessing.preprocessing()
            data_df = self.extract_data.create_final_df(network_adjusted)
            # data_df.to_csv("data_df.csv")
            d_id_title, d_title_id = self.extract_data.find_dicts(data_df)
            views_df = self.extract_data.create_views_df(data_df)
            return network, network_adjusted, df_types, data_df, d_id_title, d_title_id, views_df
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def process_files(self):
        self.logger.info("process_files")
        network, network_adjusted, df_types, data_df, d_id_title, d_title_id, views_df = \
            self.organize_data()
        self.network = network
        self.network_adjusted = network_adjusted
        self.df_types = df_types
        self.data_df = data_df
        self.d_id_title = d_id_title
        self.d_title_id = d_title_id
        self.views_df = views_df
