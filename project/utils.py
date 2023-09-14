import cfpq_data
import networkx as nx
from typing import Tuple
from pathlib import Path


def load_graph(name: str) -> nx.MultiDiGraph:
    path = cfpq_data.download(name)
    return cfpq_data.graph_from_csv(path)


def get_graph_data(graph: nx.MultiDiGraph):
    labels = set([b for _, _, _, b in graph.edges(data="label", keys=True)])
    return graph.number_of_nodes(), graph.number_of_edges(), labels


def create_labeled_two_cycle_graph(
    num_first_cycle_nodes: int, num_second_cycle_nodes: int, labels: Tuple[str, str]
) -> nx.MultiDiGraph:
    return cfpq_data.labeled_two_cycles_graph(
        num_first_cycle_nodes, num_second_cycle_nodes, labels=labels
    )


def write_to_dot(graph: nx.MultiDiGraph, path: Path):
    agraph = nx.nx_agraph.to_agraph(graph)
    agraph.write(str(path))
