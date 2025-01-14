import filecmp
import pytest
from project.graph_utils import *
import os
import cfpq_data
from pathlib import Path


class TestsGraphUtils:
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

        assert filecmp.cmp(path, path_compare)

        os.remove(path)
        os.remove(path_compare)
