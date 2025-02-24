from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Literal
import pandas as pd

from jaal.tree_builder.utils import wrap_text

@dataclass
class RelationNode():
    id: str

    relation: str | None =None
    nuclearity: Literal['S', 'N'] | None =None
    numerical_id: int | None =None # NOTE where is it used?
    level: int =0
    annotator: str | None =None
    edus: list[int] =field(default_factory=list)
    edu_index: int =0
    # shape: str # NOTE can be defined based on 'is_leaf'
    #  'font': {'multi': True},  # Enable multiline support = based on 'is_leaf'
    is_leaf: bool =False

    label: str =''

@dataclass 
class Edge():
    child: str
    parent: str


class TreeBuilder():
    def __init__(self, nodes: list[RelationNode] =[], edges: list[Edge] =[], root_id: str ='', segments: list[str] =[], satellite_node_ids: list[str] =[]):
        self.nodes = nodes
        self.edges = edges
        self.root_id = root_id
        self.segments = segments
        self.satellite_node_ids = satellite_node_ids

    def build(self):
        self.redirect_edges()
        self.assign_depth_levels()
        self.attach_child_nodes()
        self.populate_edus()  

        nodes_df = self.nodes_to_dataframe()
        edges_df = self.edges_to_dataframe() 
        return nodes_df, edges_df

    def attach_child_nodes(self):
        edges_c2p = self.edges_as_c2p_dict()
        child_nodes = edges_c2p.keys()
        parent_nodes = edges_c2p.values()
        leaf_nodes = child_nodes - parent_nodes  # Nodes without children

        for leaf_id in leaf_nodes:
            leaf_node = next(node for node in self.nodes if node.id == leaf_id)
            
            edu_index = leaf_node.edu_index  # Since leaves only have one EDU
            edu_text = f"{edu_index + 1}. {self.segments[edu_index]}"

            wrapped_text = wrap_text(edu_text)

            edu_node = RelationNode(
                id=f'{leaf_id}_edu',
                edu_index=edu_index,
                level=leaf_node.level + 1,
                annotator=leaf_node.annotator,
                is_leaf=True,
                label=wrapped_text
            )
            self.nodes.append(edu_node)
            
            edu_edge = Edge(
                child=edu_node.id,
                parent=leaf_id
            )
            self.edges.append(edu_edge)

        # nodes.extend(new_nodes)
        # return nodes, edges
    
    def populate_edus(self):
        node_lookup = {node.id: node for node in self.nodes}

        for node in self.nodes:
            if node.is_leaf:
                node.edus = [node.edu_index]
            else:
                node.edus = []

        parent_to_children = self.edges_as_p2c_dict()

        processed_nodes = set()
        for node in self.nodes:
            node.edus = self._collect_edus(node.id, node_lookup, parent_to_children, processed_nodes)

        # return nodes
    
    # TODO move to ConstituentTreeBuilder
    def assign_depth_levels(self):
        """Performs Breadth First Search to assign tree depth level to each node."""
        edges_c2p_dict = self.edges_as_p2c_dict()
        levels = {}
        queue = deque([(self.root_id, 0)])  # Each element is (node_id, level)

        while queue:
            node, level = queue.popleft()
            levels[node] = level

            for child in edges_c2p_dict.get(node, []):
                queue.append((child, level + 1))

        for node in self.nodes:
            node.level = levels[node.id]
    
    # TODO move to ConstituentTreeBuilder
    def redirect_edges(self, satellites: list[str] =[]) -> None:
        """Replaces the parent by the grandparent for each satellite node according to the structure of a constituent tree."""
        edges_c2p_dict = self.edges_as_c2p_dict()

        for edge in self.edges:
            if edge.child in self.satellite_node_ids:
                parent = edge.parent
                grandparent = edges_c2p_dict.get(parent)
                if grandparent is not None:
                    edge.parent = grandparent

    def _collect_edus(self, node_id, node_lookup, parent_to_children, processed):
        """Recursively collect EDUs for a given node."""
        if node_id in processed:
            return node_lookup[node_id].edus  # Avoid redundant computation
        
        collected_edus = list(node_lookup[node_id].edus)

        if node_id in parent_to_children:  # If the node has children
            for child_id in parent_to_children[node_id]:
                child_edus = self._collect_edus(child_id, node_lookup, parent_to_children, processed)  # Get child's 'edus'
                collected_edus.extend(child_edus)

            collected_edus.sort()
        
        node_lookup[node_id].edus = collected_edus
        processed.add(node_id)
        return collected_edus
    
    def edges_as_p2c_dict(self) -> dict:
        """Converts a list of edges to a dictionary map from parent to children IDs as values."""
        p2c_map = {}
        for edge in self.edges:
            p2c_map.setdefault(edge.parent, []).append(edge.child)

        print(self.edges)
        print(p2c_map)

        return p2c_map

    def edges_as_c2p_dict(self) -> dict:
        """Converts a list of edges to a dictionary with child IDs as keys and parent IDs as values."""
        p2c_map = {}
        for edge in self.edges:
            p2c_map[edge.child] = edge.parent
        return p2c_map

    def edges_to_dataframe(self) -> pd.DataFrame:
        """Converts a list of edges to a DataFrame with columns 'from' and 'to'."""
        data = [{"from": edge.child, "to": edge.parent} for edge in self.edges]
        return pd.DataFrame(data)
    
    def nodes_to_dataframe(self):
        """Converts a list of nodes to a DataFrame with columns named after node fields."""
        return pd.DataFrame([node.__dict__ for node in self.nodes])

