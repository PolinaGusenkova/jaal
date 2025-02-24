from pathlib import Path
import pandas as pd

from jaal.jaal import Jaal
from jaal.jaal.annotator_agreement import AnnotatorAgreement
from jaal.jaal.datasets import load_got
from jaal.rs3_parser_ import RS3Parser

def main():
    # load the data
    annotations = {
        'annotator_1': Path('/Users/pg/Documents/thesis/rs3_parser/Corpus_Clean/1/1-21-2-18-a2.rs3'),
        'annotator_2': Path('/Users/pg/Documents/thesis/rs3_parser/Corpus_Clean/2/1-21-2-18-a2.rs3')
        # 'annotator_1': Path('/Users/pg/Documents/thesis/rs3_parser/Corpus_Clean/demo1_1-21-2-18-a2.rs3'),
        # 'annotator_2': Path('/Users/pg/Documents/thesis/rs3_parser/Corpus_Clean/demo2_1-21-2-18-a2.rs3')
    }

    rs3_parser = RS3Parser()
    node_df, edge_df = rs3_parser.parse_files(annotations)
    # print("Main: ", node_df.columns)
    # print("Done")
    # exit()

    node_df = AnnotatorAgreement().find_agreements(node_df)
    # TODO check result for badly assigned node edus, or whatever the issue with wrong agreement highlight is
    # print(node_df)

    # define vis options
    vis_opts = {
        'height': '600px', # change height
        'interaction': {'hover': True}, # turn on-off the hover 
        'physics': {'enabled': False},
        'layout': {
            'hierarchical': {
                # 'enabled': False,
                'enabled': True,
                'direction': 'UD',
                'sortMethod': 'hubsize',
                'shakeTowards': 'roots',
                'parentCentralization': False,
                'levelSeparation': 100,  # More vertical space between levels
                'nodeSpacing': 150,
                'blockShifting': True,  # Compact layout
                'edgeMinimization': False,  # Allow freer positioning
            }
        },
        'nodes': {
            'font': {'multi': True},  # Enable multiline text for wrapped EDU nodes
            # 'fixed': {'x': True, 'y': False}
        },
        'edges': {
            'smooth': False  # Dashed edges for special nodes
        }
    }
                # 'physics':{'stabilization':{'iterations': 100}}} # define the convergence iteration of network

    # init Jaal and run server (with opts)
    Jaal(edge_df, node_df).plot(directed=True, vis_opts=vis_opts)

if __name__ == "__main__":
    main()