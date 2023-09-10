import pytest
from project.utils import *
import os
import cfpq_data
import networkx as nx
import pydot
from pathlib import Path


class TestsUtils:
    def test_download_graph(self):
        graph = load_graph("skos")
        assert graph.number_of_nodes() == 144
        assert graph.number_of_edges() == 252

    def test_download_graph_fails(self):
        with pytest.raises(FileNotFoundError):
            load_graph("TylerDerden")

    def test_get_graph_data(self):
        graph = load_graph("generations")
        graph_data = get_graph_data(graph)
        assert graph_data[0] == 129
        assert graph_data[1] == 273
        assert graph_data[2] == {
            "intersectionOf",
            "versionInfo",
            "someValuesFrom",
            "equivalentClass",
            "inverseOf",
            "range",
            "onProperty",
            "oneOf",
            "hasSex",
            "hasSibling",
            "sameAs",
            "hasChild",
            "rest",
            "first",
            "hasParent",
            "hasValue",
            "type",
        }

    def test_create_labeled_two_cycle_graph(self):
        graph = create_labeled_two_cycle_graph(2, 2, ("a", "b"))
        assert graph.number_of_nodes() == 5
        assert graph.number_of_edges() == 6

    def test_write_to_dot(self):
        num_first_cycle_nodes = 2
        num_second_cycle_nodes = 2
        labels = ("a", "b")
        path = Path("graph.dot")
        path_compare = Path("graph_compare.dot")

        graph = create_labeled_two_cycle_graph(
            num_first_cycle_nodes, num_second_cycle_nodes, labels
        )
        write_to_dot(graph, path)

        graph_compare = cfpq_data.labeled_two_cycles_graph(
            num_first_cycle_nodes, num_second_cycle_nodes, labels=labels
        )
        write_to_dot(graph_compare, path_compare)

        def read(input_path: Path):
            return open(input_path, "r").read()

        assert read(path) == read(path_compare)

        graph_from_pydot = nx.nx_pydot.from_pydot(pydot.graph_from_dot_file(path)[0])
        graph_compare_from_pydot = nx.nx_pydot.from_pydot(
            pydot.graph_from_dot_file(path_compare)[0]
        )

        assert (
            graph_from_pydot.number_of_nodes()
            == graph_compare_from_pydot.number_of_nodes()
        )
        assert (
            graph_from_pydot.number_of_edges()
            == graph_compare_from_pydot.number_of_edges()
        )

        os.remove(path)
        os.remove(path_compare)
