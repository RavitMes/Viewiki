from sklearn.preprocessing import MinMaxScaler
import logging
import pandas as pd

class SNA:
    def __init__(self, views_df, df_types, d_id_title, d_title_id, network):
        self.logger = logging.getLogger(__name__)
        self.views_df = views_df
        self.df_types = df_types
        self.d_id_title = d_id_title
        self.d_title_id = d_title_id
        self.network = network

    def create_df_nodes(self):
        self.logger.info("create_df_nodes")
        try:
            self.logger.info(f"creates total views curves graph")
            dict_index_type = self.create_dict_id_link_type()
            print("dict_index_type", len(dict_index_type), type(dict_index_type), dict_index_type)
            self.views_df["total"] = self.views_df.sum(axis=1, skipna=True)
            current = self.views_df.iloc[:, -8:-1]
            previous = self.views_df.iloc[:, :-8]
            self.views_df['avg_current_week'] = current.mean(axis=1, skipna=True)
            self.views_df['avg_previous_weeks'] = previous.mean(axis=1, skipna=True)
            self.views_df['change(cur/prev)'] = (
                        self.views_df['avg_current_week'] / self.views_df['avg_previous_weeks'])
            self.views_df['link_type'] = self.views_df.index.map(dict_index_type)
            types = list([i for i in self.views_df["link_type"].unique() if type(i) is str])
            self.logger.info(f"types: {types}")
            d_marker = {"Interlink": "s"}
            shapes = ["o","^","d","p","*"]
            for i in range(len(types)):
                if types[i]!="Interlink":
                    d_marker[types[i]]=shapes[i]

            markers = pd.DataFrame({"category":[i for i in d_marker.keys()], "marker": [i for i in d_marker.values()]})
            markers.to_csv("markers.csv")

            self.views_df['marker'] = self.views_df["link_type"].map(d_marker)
            self.views_df['title'] = self.views_df.index.map(self.d_id_title)
            scaler = MinMaxScaler()
            try:
                self.views_df['views_scaled'] = scaler.fit_transform(
                    self.views_df[['total']]) * 7000
            except ValueError:
                self.views_df['views_scaled'] = scaler.fit_transform(self.views_df[['total']])
            d_opposite_new = {}
            for k, v in self.d_title_id.items():
                k = k.replace(" ", "_")
                d_opposite_new[k] = v
            # views_df_filtered = self.views_df[
            #     (self.views_df['marker'] != 'o')]
            return self.views_df
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def create_d_title_id_new(self):
        self.logger.info("create_d_title_id_new")
        try:
            d_title_id_new = {}
            for k, v in self.d_title_id.items():
                k = k.replace(" ", "_")
                d_title_id_new[k] = v
            return d_title_id_new
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def assign_val(self, record):
        self.logger.info("assign_val")
        try:
            if str(record['id_to']) == 'nan':
                return record['id_from']
            else:
                return record['id_to']
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def create_df_network(self):
        self.logger.info("create_df_network")
        try:
            d_title_id_new = self.create_d_title_id_new()
            self.network['id_from'] = self.network['wiki_page_only'].map(d_title_id_new)
            self.network['id_to'] = self.network['page_interlink_only'].map(d_title_id_new)
            self.network['id_to2'] = self.network.apply(self.assign_val, axis=1)
            self.network.to_csv("n.csv")
            return self.network
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def create_dict_id_link_type(self):

        self.logger.info("create_dict_id_link_type")
        try:
            dict_types = self.df_types.to_dict()[0]
            dict_index_type = {}
            print("-----")
            print(dict_types)
            for k, v in dict_types.items():
                # if str(k)!='nan':
                try:
                    if str(k)!="nan":
                        k = k.replace("_", " ")
                        k = k.replace("%27", "'")
                        dict_index_type[self.d_title_id[k]] = v
                except:
                    print(k,v)
                    continue

            print("final: ", dict_index_type)
            return dict_index_type

        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")
