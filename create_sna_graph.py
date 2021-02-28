import networkx as nx
from tqdm import tqdm
import matplotlib
import logging
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import pandas as pd


def find_change_views(number):
    num_round = round(number, 2)
    change = ((num_round*100-100)/100)*100
    change = round(change,2)
    return change

def repr_change(change):
    if change>0:
        return "+"+str(change)+"%"
    else:
        return str(change)+"%"

def tweeter_graph(network, attributes, dict_labels, ax):
    logger = logging.getLogger(__name__)
    logger.info(f"creates the SNA graph")
    try:
        G = nx.from_pandas_edgelist(network, "id_from", "id_to2")
        color = {}
        shape = {}
        labels = {}
        size = {}

        for ind, row in attributes.iterrows():
            node = ind
            shape[node] = row['marker']
            color[node] = row['change(cur/prev)']
            size[node] = row['views_scaled']
        node_color = []
        node_shape = []
        node_size = []

        num_labels={}
        changes={}
        for v in tqdm(G):
            try:
                node_color.append(color[v])
                node_shape.append(shape[v])
                node_size.append(size[v] * 20)
                label = dict_labels[v]
                text = label.split()
                n = 2
                labels[v] = ' '.join([' '.join(text[i:i + n]) + "\n" for i in range(0, len(text), n)])
                spaces_num = int(len(text)/n + 1)
                change = find_change_views(color[v])
                changes[v]=change
                str_change = repr_change(change)
                num_labels[v] = "\n"*spaces_num + str_change
            except:
                logger.info(f"the node {v} not found")
                labels[v] = ""
                num_labels[v] = ""
                node_color.append(1)
                node_shape.append("o")
                node_size.append(20)

        fig = plt.figure(figsize=(40, 30))

        shapes = []
        # markers = list(attributes["marker"].unique())
        markers_df = pd.read_csv("markers.csv")
        markers = list(markers_df["marker"])
        categories = list(markers_df["category"])

        # ax_leg = fig.add_subplot(1, 1, 1)
        for i in range(len(markers)):
            logger.info(f"marker: {markers[i]}")
            logger.info(f"marker: {categories[i]}")
            marker = mlines.Line2D([], [], color='black', marker=markers[i], linestyle='None',
                                      markersize=10, label=categories[i])
            shapes.append(marker)


        pos = nx.nx_pydot.graphviz_layout(G)
        nx.draw(G, pos=pos, node_color='white', node_size=0.00000001, node_shape=',',
                edge_color='lightgray', ax=ax)

        vmin = 0.3
        vmax = 1.3
        cmap = plt.cm.coolwarm
        for v in tqdm(G):
            try:
                nx.draw_networkx_nodes(G, pos, nodelist=[v],
                                       node_size=[size[v] * 4],
                                       node_color=[color[v]],
                                       node_shape=shape[v],
                                       cmap=cmap,
                                       vmin=vmin,
                                       vmax=vmax,
                                       edgecolors='black',
                                       alpha=0.7,
                                       ax=ax)
            except Exception as exp:
                logger.info("exception: ", exp.args)
                continue


        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=min(changes.values()), vmax=max(changes.values())))
        cbar = plt.colorbar(sm, fraction=0.046, pad=0.04, ax=ax)
        cbar.ax.get_yaxis().labelpad = 50
        cbar.ax.set_ylabel('average_views_current_week / average_views_previous_weeks',
                           rotation=270)
        cbar.ax.tick_params(labelsize=40)
        text = ax.yaxis.label
        font = matplotlib.font_manager.FontProperties(family='times new roman', style='italic',
                                                      size=22)
        text.set_font_properties(font)


        nx.draw_networkx_labels(G, pos, labels=labels, font_color='black', font_size=22, ax=ax)
        nx.draw_networkx_labels(G, pos, labels=num_labels, font_color='red', font_size=22, ax=ax)

        ax.legend(handles=shapes,prop={'size': 22}, fontsize=22)
        plt.savefig("fig.png")

        return fig

    except Exception as err:
        print("exp, ", err.args)
        logger.info(f"encounter error: {str(err), err.args}")
