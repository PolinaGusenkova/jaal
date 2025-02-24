from enum import Enum

DEFAULT_EDGE_COLOR = "#FFFFFF"
HIGHLIGHTED_EDGE_COLOR = "#676767"

EDU_BACKGROUND_COLOR = "#FFFFFF"
HIGHLIGHTED_NODE_COLOR = "#dc143c"

DEFAULT_NODE_SIZE = 15

DEFAULT_EDGE_SIZE = 1
HIGHLIGHTED_EDGE_SIZE = 4


class EntityType(Enum):
    HUB = "hub"
    LNK = "link"
    NHL = "non_historized_link"
    # Internal type - highlight on condition
    LNK_WITH_2_CONNECTIONS = "link_with_2_connections"