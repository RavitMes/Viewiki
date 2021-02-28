import matplotlib.pyplot as plt
import logging


def create_views_curves_graph(titles, views_df, d_id_title, ax):
    logger = logging.getLogger(__name__)
    logger.info(f"creates total views curves graph")
    try:
        fig = plt.figure(figsize=(30, 20))
        for idx in titles:
            link_id = idx
            ax.plot(views_df.columns, views_df.loc[link_id, :], label=d_id_title[link_id])
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
        ax.legend()
        ax.set_ylabel("number of views")
        ax.set_xlabel("date")
        return fig
    except Exception as err:
        logger.info(f"encounter error: {str(err), err.args}")
