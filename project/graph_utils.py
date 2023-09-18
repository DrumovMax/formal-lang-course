import cfpq_data
import networkx as nx
from typing import Tuple
from pathlib import Path


def load_graph(name: str) -> nx.MultiDiGraph:
    """Loads a graph from dataset by name.

    Parameters:
    ----------
    name: str
        Name of graph from cfpq dataset.

    Returns:
    ---------
    graph: nx.MultiDiGraph
        Loaded graph.
    """
    path = cfpq_data.download(name)
    return cfpq_data.graph_from_csv(path)


def get_graph_data(graph: nx.MultiDiGraph):
    """Get information about the graph: number of nodes, number of edges and set of labels.

    Parameters:
    ----------
    graph: nx.MultiDiGraph
        Graph, information on which we will get.

    Returns:
    ---------
    result: tuple[number of edges, number of nodes, set of labels]
        Loaded graph info.
    """
    labels = set([b for _, _, _, b in graph.edges(data="label", keys=True)])
    return graph.number_of_nodes(), graph.number_of_edges(), labels


def create_labeled_two_cycle_graph(
    num_first_cycle_nodes: int, num_second_cycle_nodes: int, labels: Tuple[str, str]
) -> nx.MultiDiGraph:
    """Create labeled two cycles graph.

    Parameters:
    ----------
    num_first_cycle_nodes: int
        The number of nodes in the first cycle without a common node.
    num_second_cycle_nodes: int
        The number of nodes in the second cycle without a common node.
    labels: Tuple[str, str]
        Labels that will be used to mark the edges of the graph.

    Returns:
    ---------
    graph: nx.MultiDiGraph
        Returns a graph with two cycles connected by one node. With labeled edges.
    """
    return cfpq_data.labeled_two_cycles_graph(
        num_first_cycle_nodes, num_second_cycle_nodes, labels=labels
    )


def write_to_dot(graph: nx.MultiDiGraph, path: Path):
    """Write graph to dot file.

    Parameters:
    ----------
    graph: nx.MultiDiGraph
        The graph that will be written to the dot file.
    path: Path
        The name of the file to which the graph will be written.
    """
    agraph = nx.nx_agraph.to_agraph(graph)
    agraph.write(str(path))
