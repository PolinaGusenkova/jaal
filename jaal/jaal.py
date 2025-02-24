"""
Author: Mohit Mayank

Main class for Jaal network visualization dashboard
"""

import copy
import json
import logging

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from jaal.jaal.entity_styles import (
    DEFAULT_EDGE_COLOR,
    HIGHLIGHTED_NODE_COLOR,
    EntityType,
)
from jaal.jaal.layout_ import (
    DEFAULT_BORDER_SIZE,
    DEFAULT_EDGE_SIZE,
    DEFAULT_NODE_SIZE,
    DEFAULT_NODE_COLOR,
    HIGHLIGHTED_EDGE_COLOR,
    create_color_legend,
    get_app_layout,
    get_distinct_colors,
)
from jaal.jaal.parse_dataframe import parse_dataframe
from utils import DEFAULT_OPTIONS, OVERLAY_OPTIONS

_LOGGER = logging.getLogger(__name__)

# TODO add 'dashes' to edges and 'color' to nodes to change it for 'edu'=True/False

# class
class Jaal:
    """The main visualization class"""

    def __init__(self, edge_df, node_df=None):
        """
        Parameters
        -------------
        edge_df: pandas dataframe
            The network edge data stored in format of pandas dataframe

        node_df: pandas dataframe (optional)
            The network node data stored in format of pandas dataframe
        """
        _LOGGER.debug("Parsing the data...")
        self.data, self.scaling_vars = parse_dataframe(edge_df, node_df)
        self.filtered_data = self.data.copy()
        self.original_data = self._set_default_styles(copy.deepcopy(self.data))
        self.node_value_color_mapping = {}
        self.edge_value_color_mapping = {}
        _LOGGER.debug("Done")

    def _callback_search_graph(self, graph_data, search_text):
        """Hide the nodes unrelated to search quiery"""
        nodes = graph_data['nodes']
        for node in nodes:
            if search_text.lower() not in node['label'].lower():
                node["color"] = {"border": HIGHLIGHTED_EDGE_COLOR}
                node["borderWidth"] = DEFAULT_BORDER_SIZE + 2
            else:
                node["color"] = {"border": DEFAULT_EDGE_COLOR}
                node["borderWidth"] = DEFAULT_BORDER_SIZE
        graph_data['nodes'] = nodes
        return graph_data

    def _set_default_styles(self, graph_data):
        """Set the graph style to the defaults."""
        # for node in graph_data["nodes"]:
        #     node['hidden'] = False

        #     node["borderWidth"] = DEFAULT_BORDER_SIZE

        #     # node_type = EntityType(node["object_type"])
        #     # node["image"]["unselected"] = unselected_node_image_url[node_type]

        # for edge in graph_data["edges"]:
        #     # pass
        #     # edge["hidden"] = False
        #     # edge["color"] = {"color": DEFAULT_EDGE_COLOR}
        #     edge["color"] = DEFAULT_EDGE_COLOR
        #     edge["width"] = DEFAULT_EDGE_SIZE
        return graph_data
    
    def _callback_overlay(self, graph_data, overlay, current_options):
        print(f"_callback_overlay: {overlay}")

        if not overlay:
            return graph_data, DEFAULT_OPTIONS  # Reset to default view if overlay is disabled

        # Force overlay: modify node levels for proper alignment
        # for node in graph_data["nodes"]:
        #     if "level" in node:
        #         node["level"] = self._get_aligned_level(node["id"])  # 🔥 Ensure level alignment

        # Adjust layout settings for proper overlaying
        updated_options = OVERLAY_OPTIONS.copy()
        updated_options["layout"]["hierarchical"].update({
            "treeSpacing": 0,  # Bring trees together
            "nodeSpacing": 10,  # Minimize spacing for better overlay
            "parentCentralization": True,  # Align roots together
            "blockShifting": False,  # Prevent shifting nodes sideways
            "edgeMinimization": True,  # Reduce edge overlap
        })

        return graph_data, updated_options
    
    def _callback_agreement(self, graph_data, overlay):
        print(f"_callback_agreement: {overlay}")
        for node in graph_data['nodes']:
            if overlay:
                if node["agreement"] and not node["is_leaf"]:
                    node["color"] = {"border": HIGHLIGHTED_NODE_COLOR}
                    node["borderWidth"] = DEFAULT_BORDER_SIZE + 2
                    node["title"] = node["agreement"]
                    # node["label"] = node["agreement"]
                    # node["color"] = HIGHLIGHTED_NODE_COLOR
                    # node["color"] = HIGHLIGHTED_NODE_COLOR
            else:
                # node["color"] = {"border": DEFAULT_EDGE_COLOR}
                # node["borderWidth"] = DEFAULT_BORDER_SIZE
                return self.data

        return graph_data

    def _callback_select_annotator(self, graph_data, annotator):
        print(f"_callback_select_annotator: {annotator}")
        for node in graph_data['nodes']:
            if annotator == 'All' or node['annotator'] == annotator:
                node['hidden'] = False
            elif node['annotator'] != annotator:
                node['hidden'] = True
        return graph_data
    
    def _callback_tree_type(self, graph_data, tree_type):
        print(f"_callback_tree_type: {tree_type}")
        return graph_data

    def get_color_popover_legend_children(self, node_value_color_mapping=None, edge_value_color_mapping=None):
        """Get the popover legends for node and edge based on the color setting"""
        # var
        if edge_value_color_mapping is None:
            edge_value_color_mapping = {}
        if node_value_color_mapping is None:
            node_value_color_mapping = {}
        popover_legend_children = []

        # common function
        def create_legends_for(title="Node", legends=None):
            # add title
            if legends is None:
                legends = {}
            _popover_legend_children = [dbc.PopoverHeader(f"{title} legends")]
            # add values if present
            if len(legends) > 0:
                for key, value in legends.items():
                    _popover_legend_children.append(
                        # dbc.PopoverBody(f"Key: {key}, Value: {value}")
                        create_color_legend(key, value)
                    )
            else:  # otherwise add filler
                _popover_legend_children.append(dbc.PopoverBody(f"no {title.lower()} colored!"))
            return _popover_legend_children

        # add node color legends
        popover_legend_children.extend(create_legends_for("Node", node_value_color_mapping))
        # add edge color legends
        popover_legend_children.extend(create_legends_for("Edge", edge_value_color_mapping))
        return popover_legend_children

    import pandas as pd
    
    def create(self, directed=False, vis_opts=None):
        """Create the Jaal app and return it

        Parameter
        ----------
            directed: boolean
                process the graph as directed graph?

            vis_opts: dict
                the visual options to be passed to the dash server (default: None)

        Returns
        -------
            app: dash.Dash
                the Jaal app
        """
        # create the app
        app = dash.dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

        # define layout
        app.layout = get_app_layout(  # type: ignore[misc]
            self.data, color_legends=self.get_color_popover_legend_children(), directed=directed, vis_opts=vis_opts
        )

        # create callbacks to toggle hide/show sections - FILTER section
        @app.callback(
            Output("filter-show-toggle", "is_open"),
            [Input("filter-show-toggle-button", "n_clicks")],
            [State("filter-show-toggle", "is_open")],
        )
        def toggle_filter_collapse(n, is_open):
            if n:
                return not is_open
            return is_open
        
        @app.callback(
            Output("graph", "data"),
            [
                Input("overlay_checkbox", "checked"),
                Input("annotator", "value"),
                Input("view_toggle", "value"),
            ],
            [
                State("graph", "data"),
                # State("graph", "options"),
            ],
        )
        def update_graph(overlay, annotator, tree_type, graph_data):
            ctx = dash.callback_context

            if not ctx.triggered:
                raise PreventUpdate

            input_id = ctx.triggered[0]["prop_id"].split(".")[0]

            # graph_data = self.enforce_leaf_order(graph_data)
            # updated_options = current_options.copy()  # <<<<< Ensure we modify a copy

            if input_id == "overlay_checkbox":
                graph_data = self._callback_agreement(graph_data, overlay)
                # print(graph_data["nodes"])


            elif input_id == "annotator":
                graph_data = self._callback_select_annotator(graph_data, annotator)

            elif input_id == "view_toggle":
                graph_data = self._callback_tree_type(copy.deepcopy(self.original_data), tree_type)

            else:
                graph_data = self.data
                # self.enforce_leaf_order(graph_data)

            # graph_data = copy.deepcopy(self.original_data)
            # elif input_id == "search_graph":
            #     if n_clicks_search > 0 and search_text:
            #         graph_data = self._callback_search_graph(copy.deepcopy(self.original_data), search_text)
            #     else:
            #         graph_data = copy.deepcopy(self.original_data)

            return graph_data  # <<<<< Ensure options are updated

        return app

    def plot(self, debug=False, host="127.0.0.1", port=8050, directed=False, vis_opts=None):
        """Plot the Jaal by first creating the app and then hosting it on default server

        Parameter
        ----------
            debug (boolean)
                run the debug instance of Dash?

            host: string
                ip address on which to run the dash server (default: 127.0.0.1)

            port: string
                port on which to expose the dash server (default: 8050)

            directed (boolean):
                whether the graph is directed or not (default: False)

            vis_opts: dict
                the visual options to be passed to the dash server (default: None)
        """
        # call the create_graph function
        app = self.create(directed=directed, vis_opts=vis_opts)
        # run the server
        app.run_server(debug=debug, host=host, port=port)
