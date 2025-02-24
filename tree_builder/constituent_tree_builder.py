from collections import deque
from jaal.tree_builder.tree_builder import TreeBuilder


class ConstituentTreeBuilder(TreeBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def redirect_edges(self) -> None:
        """Replaces the parent by the grandparent for each satellite node according to the structure of a constituent tree."""
        edges_c2p_dict = self.edges_as_c2p_dict()

        for edge in self.edges:
            if edge.child in self.satellite_node_ids:
                parent = edge.parent
                grandparent = edges_c2p_dict.get(parent)
                if grandparent is not None:
                    edge.parent = grandparent

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

