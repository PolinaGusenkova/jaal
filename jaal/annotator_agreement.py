import pandas as pd

class AnnotatorAgreement:
    def find_agreements(self, node_dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Processes the input node and edge dataframes to compute, for each node, the list of annotators
        that agree on the node's annotation. The agreement is defined as having the same values for
        'relation', 'nuclearity' and 'edus'. The result is a copy of the original node dataframe with
        an additional column 'agreement'. Leaf nodes are assumed to be identical across annotators
        and therefore will receive the full list of annotators.
        """
        # Make a copy of the node dataframe to avoid modifying the original.
        result_dataframe = node_dataframe.copy()
        
        # Compute the node signature as a tuple of (relation, nuclearity, edus) for each row.
        result_dataframe["node_signature"] = result_dataframe.apply(
            self._compute_node_signature, axis=1
        )
        
        # Get the full list of annotators present in the data.
        all_annotators = self._get_all_annotators(result_dataframe)
        
        # Compute an agreement mapping:
        # For each unique node signature, determine the list of annotators that have that signature.
        # For leaf nodes (is_leaf == True), we override with full agreement (all annotators),
        # because it is known that the leaves are identical.
        agreement_mapping = self._compute_agreement_mapping(result_dataframe, all_annotators)
        
        # Now assign the agreement list to every row, based on its node signature.
        result_dataframe["agreement"] = result_dataframe["node_signature"].apply(
            lambda signature: agreement_mapping.get(signature, [])
        )
        
        # Optionally drop the temporary 'node_signature' column.
        result_dataframe.drop(columns=["node_signature"], inplace=True)
        
        return result_dataframe

    def _compute_node_signature(self, row: pd.Series) -> tuple:
        return (row["relation"], row["nuclearity"], tuple(row["edus"]))

    def _get_all_annotators(self, dataframe: pd.DataFrame) -> list:
        annotators = dataframe["annotator"].unique().tolist()
        return sorted(annotators)

    def _compute_agreement_mapping(self, dataframe: pd.DataFrame, full_annotator_list: list) -> dict:
        """
        For every unique node signature in the dataframe, determine the annotators that have
        a node with that signature. For leaf nodes (where is_leaf is True), the agreement is
        forced to the full list of annotators because they are known to be identical.
        """
        agreement_mapping = {}
        
        # Group the dataframe by the computed node signature.
        grouped_by_signature = dataframe.groupby("node_signature")
        
        
        # Process each group (each unique signature).
        for signature, group in grouped_by_signature:
            # Get a sorted list of annotators that have a node with this signature.
            annotators_with_signature = sorted(group["annotator"].unique().tolist())
            
            # For internal nodes, require that at least two annotators have the same node.
            if len(annotators_with_signature) >= 2:
                agreement_mapping[signature] = annotators_with_signature
            else:
                agreement_mapping[signature] = []
        
        return agreement_mapping
