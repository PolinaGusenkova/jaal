from collections import defaultdict, deque
from operator import concat
from pathlib import Path
from xml.dom import NotFoundErr
import xml.etree.ElementTree as ET
import pandas as pd

from jaal.tree_builder.tree_builder import Edge, RelationNode
from jaal.tree_builder.tree_builder import TreeBuilder


class RS3Parser():
    def __init__(self):
        pass

    def parse_files(self, files: dict[str,Path]):
        nodes = pd.DataFrame()
        edges = pd.DataFrame()
        for annotator, file in files.items():
            annotator_nodes, annotator_edges = self.parse(file, annotator)
            nodes = pd.concat([nodes, annotator_nodes], ignore_index=True)
            edges = pd.concat([edges, annotator_edges], ignore_index=True)

        return nodes, edges
        
    def parse(self, file, annotator: str):
        xml_tree = ET.parse(file)
        relations = xml_tree.getroot().find("header/relations")
        body = xml_tree.getroot().find("body")

        if relations is None:
            raise NotFoundErr("<relations> tag not found in the XML.")
        if body is None:
            raise NotFoundErr("<body> tag not found in the XML.")
        
        relation_type = {}
        for relation in list(relations):
            nuclearity = 'S' if relation.get('type') == 'rst' else 'N'
            relation_type[relation.get('name')] = nuclearity
        relation_type['span'] = 'N'

        items = list(body)

        def leaf():
            return item.tag == 'segment'

        edus: list[str|None] = []
        nodes: list[RelationNode] = []
        edges: list[Edge] = []
        satellites: list[str] = []
        
        for item in items:  
            edu_index = len(edus)
            if leaf():
                edus.append(item.text)

            node_id = f'{item.get('id')}_{annotator}' if item.get('id') is not None else ''
            num_id = int(item.get('id', 0))

            child_node_id = f'{item.get('id')}_{annotator}'
            parent_node_id = f'{item.get('parent')}_{annotator}' if item.get('parent') else 'root'

            new_edge = Edge(
                child=child_node_id,
                parent=parent_node_id
            )
            edges.append(new_edge)

            new_node = RelationNode(
                relation=item.get('relname'),
                nuclearity=relation_type.get(item.get('relname')),
                id=node_id,
                numerical_id=num_id,
                level=0,
                annotator=annotator,
                edus=[],
                edu_index=edu_index,
                is_leaf=False
            )
            nodes.append(new_node)

            if new_node.nuclearity:
                if new_node.nuclearity == 'S':
                    satellites.append(new_node.id)
                new_node.label = f"{new_node.relation}, {new_node.nuclearity}" # + ', ' + item.get('id')
            else:
                root_id = new_node.id
                new_node.label = 'root'

        tree_builder = TreeBuilder(
            nodes=nodes,
            edges=edges,
            root_id=root_id,
            segments=edus,
            satellite_node_ids=satellites
        )

        nodes_df, edges_df = tree_builder.build()
        return nodes_df, edges_df