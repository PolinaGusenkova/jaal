from dataclasses import dataclass, field
from typing import Literal

from pandas import DataFrame
from jaal.tree_builder.tree_builder import TreeBuilder
from jaal.tree_builder.utils import wrap_text

class RS3TreeBuilder(TreeBuilder):
    def __init__(self):
        self.nodes = []
        self.edges = []

        self.nodes_df = DataFrame()
        self.edges_df = DataFrame()

    def add_node(self, node):
        self.nodes

    def attach_child_nodes(self, nodes: list, edges: dict, edus):
        child_nodes = edges.keys()
        parent_nodes = edges.values()
        leaf_nodes = child_nodes - parent_nodes  # Nodes without children

        new_nodes = []
        new_edges = []

        for leaf_id in leaf_nodes:
            leaf_node = next(node for node in nodes if node.id == leaf_id)
            
            edu_index = leaf_node.edu_index  # Since leaves only have one EDU
            edu_text = f"{edu_index + 1}. {edus[edu_index]}"

            wrapped_text = wrap_text(edu_text)

            edu_node = RelationNode(
                id=f'{leaf_id}_edu',
                edu_index=edu_index,
                level=leaf_node.level + 1,
                annotator=leaf_node.annotator,
                is_leaf=True,
                label=wrapped_text
            )
            new_nodes.append(edu_node)

            edges[edu_node.id] = leaf_id

        nodes.extend(new_nodes)

        return nodes, edges