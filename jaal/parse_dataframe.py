"""
Author: Mohit Mayank

Parse network data from dataframe format into visdcc format
"""


from jaal.jaal.entity_styles import DEFAULT_NODE_SIZE, EDU_BACKGROUND_COLOR
from jaal.jaal.layout_ import get_distinct_colors


def compute_scaling_vars_for_numerical_cols(df):
    """Identify and scale numerical cols"""
    # identify numerical cols
    numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
    numeric_cols = df.select_dtypes(include=numerics).columns.tolist()
    # var to hold the scaling function
    scaling_vars = {}
    # scale numerical cols
    for col in numeric_cols:
        minn, maxx = df[col].min(), df[col].max()
        scaling_vars[col] = {"min": minn, "max": maxx}
        # return
    return scaling_vars


def parse_dataframe(edge_df, node_df=None):
    """Parse the network dataframe into visdcc format

    Parameters
    -------------
    edge_df: pandas dataframe
            The network edge data stored in format of pandas dataframe

    node_df: pandas dataframe (optional)
            The network node data stored in format of pandas dataframe
    """
    # Data checks
    # Check 1: mandatory columns presence
    if ("from" not in edge_df.columns) or ("to" not in edge_df.columns):
        msg = "Edge dataframe missing either 'from' or 'to' column."
        raise ValueError(msg)
    # Check 2: if node_df is present, it should contain 'node' column
    if node_df is not None:
        if "id" not in node_df.columns:
            msg = "Node dataframe missing 'id' column."
            raise ValueError(msg)

    # Data post-processing - convert the from and to columns in edge data as string for searching
    edge_df[["from", "to"]] = edge_df[["from", "to"]].astype(str)
    # edge_df.loc[:, ["from", "to"]] = edge_df.loc[:, ["from", "to"]].astype(str)

    # Data pot processing (scaling numerical cols in nodes and edge)
    scaling_vars = {"node": None, "edge": None}
    if node_df is not None:
        scaling_vars["node"] = compute_scaling_vars_for_numerical_cols(node_df)
    scaling_vars["edge"] = compute_scaling_vars_for_numerical_cols(edge_df)

    # create node list w.r.t. the presence of absence of node_df
    nodes = []
    if node_df is None:
        node_list = list(set(edge_df["from"].unique().tolist() + edge_df["to"].unique().tolist()))
        nodes = [
            {"id": node_name, "label": node_name, "shape": "dot", "size": 7}
            for node_name in node_list
        ]
    else:
        # convert the node id column to string
        node_df["id"] = node_df["id"].astype(str)
        # if title is not present, make it same as label
        # if "title" not in node_df.columns:
        #     node_df["title"] = node_df["id"]
        ################
        # node_df["title"] = node_df["id"]
        ################
        # see if node imge url is present or not
        node_image_url_flag = "node_image_url" in node_df.columns
        selected_node_image_url_flag = "selected_node_image_url" in node_df.columns
        # set color mapping
        if not node_image_url_flag:
            annotators = node_df['annotator'].dropna().unique().tolist()
            colors = get_distinct_colors(len(annotators))
            annotator_color_map = dict(zip(annotators, colors))
            node_df['color'] = node_df['annotator'].map(lambda x: annotator_color_map.get(x, "#CCCCCC")) 
        
        # create the node data
        nodes_with_children = set(edge_df["to"]) # collect nodes with outgoing edges, e.g. children

        for node in node_df.to_dict(orient="records"):
            node["is_leaf"] = node["id"] not in nodes_with_children
            leaf_shape = "box"
            # leaf_color = EDU_BACKGROUND_COLOR

            node["color"] = EDU_BACKGROUND_COLOR if node["is_leaf"] else node["color"]

            if not node_image_url_flag:
                nodes.append({
                    **node, 
                    **{
                        # "label": node["title"], 
                        "shape": leaf_shape if node["is_leaf"] else "dot", 
                        "size": DEFAULT_NODE_SIZE                    }
                })
            else:
                image_settings = {"unselected": node["node_image_url"]}
                if selected_node_image_url_flag:
                    image_settings["selected"] = node["selected_node_image_url"]
                nodes.append({
                    **node, 
                    **{
                        # "label": node["title"], 
                        "shape": leaf_shape if node["is_leaf"] else "circularImage", 
                        "image": image_settings, 
                        "size": DEFAULT_NODE_SIZE                   
                    }
                })

    # create edges from df
    # print(nodes_with_children)

    # Build edges with dashed style if the "from" node is a leaf (no outgoing edges)
    edges = [
        {
            **row,
            **{
                "id": row["from"] + "__" + row["to"],
                "color": {"color": "#97C2FC"},
                "dashes": row["from"] not in nodes_with_children  # Dashed if node is a leaf
            }
        }
        for row in edge_df.to_dict(orient="records")
    ]

    # print(edges)

    # return
    return {"nodes": nodes, "edges": edges}, scaling_vars
