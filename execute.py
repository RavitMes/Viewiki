from create_curves import create_views_curves_graph
from create_sna_tables import SNA
from create_sna_graph import tweeter_graph
import matplotlib.pyplot as plt
from matplotlib import gridspec
import io
import logging


def create_dashboard(file_handler, titles):
    logger = logging.getLogger(__name__)
    network, df_types, d_id_title, d_title_id, views_df = file_handler.network, \
                                                          file_handler.df_types, \
                                                          file_handler.d_id_title, \
                                                          file_handler.d_title_id, \
                                                          file_handler.views_df

    titles = [title for title in titles if title != ""]
    sna = SNA(views_df, df_types, d_id_title, d_title_id, network)
    fig3 = plt.figure(figsize=(40, 50))
    if len(titles)>0:
        logger.info("create dash")
        gs = gridspec.GridSpec(2, 1, height_ratios=[1, 4])
        ax1 = fig3.add_subplot(gs[0])
        create_views_curves_graph(titles, views_df, d_id_title, ax1)
        # fig3.savefig("views_curves.png")
        df_nodes = sna.create_df_nodes()
        df_network = sna.create_df_network()
        ax2 = fig3.add_subplot(gs[1])
        tweeter_graph(df_network, df_nodes, d_id_title, ax2)
        # fig3.savefig("views_curves_and_sna.png")
        plt.subplots_adjust(hspace=0.4)
        # fig3.savefig("network_wikipedia_filtered_1608.png")
    else:
        df_nodes = sna.create_df_nodes()
        df_network = sna.create_df_network()
        ax1 = fig3.add_subplot(1, 1, 1)
        tweeter_graph(df_network, df_nodes, d_id_title, ax1)

    # fig3.savefig("report.jpg")
    bytes_image = io.BytesIO()
    fig3.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    plt.close(fig3)
    plt.clf()

    return bytes_image
