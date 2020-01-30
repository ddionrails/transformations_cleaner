"""Contains Cleaner class to clean up generations files."""

from pathlib import Path
from typing import Dict, Generator, Set, Tuple

import pandas
from networkx import DiGraph
from networkx.algorithms import transitive_closure


class Cleaner:
    """Clean out non valid variables from a generations relation file.

    Attributes:
        _trash: A cache for variable nodes, that can be dropped after the
                transitive closure of the graph has been created.
    """

    _trash: Set[Tuple[str, str, str]]
    graph: DiGraph
    generations_path: Path
    version: str

    def __init__(
        self, generations_path: Path, variables_path: Path, version: str
    ) -> None:
        self._trash = set()
        self.generations_path = generations_path
        self.variables_path = variables_path
        self.version = version
        self.variables = set(self.read_variables())
        self.graph = self.get_graph()
        super().__init__()

    def filter_variables(self) -> DiGraph:
        """Remove trashed nodes from the graph."""
        for node in self._trash:
            self.graph.remove_node(node)
        self._trash = set()

        return self.graph

    def get_graph(self) -> DiGraph:
        """Load transformation content into a network graph."""
        transformations = self.read_transformations()
        graph = DiGraph()

        for relation in transformations:
            graph.add_edge(relation["input"], relation["output"])

        return transitive_closure(graph)

    def read_transformations(
        self,
    ) -> Generator[Dict[str, Tuple[str, str, str]], None, None]:
        """Parse generations/transformations.csv to workable format."""
        path = self.generations_path
        with open(path, "r", encoding="utf-8") as file:
            reader = pandas.read_csv(file, header="infer", iterator=True, chunksize=1)
            for line in reader:
                _input = (
                    line["input_study"].item(),
                    line["input_dataset"].item(),
                    line["input_variable"].item(),
                )
                _output = (
                    line["output_study"].item(),
                    line["output_dataset"].item(),
                    line["output_variable"].item(),
                )
                if line["output_version"].item() != self.version:
                    self._trash.add(_output)
                for node in [_input, _output]:
                    if node not in self.variables:
                        self._trash.add(node)
                yield {
                    "input": _input,
                    "output": _output,
                }

    def read_variables(self) -> Generator[Tuple[str, str, str], None, None]:
        """Parse variable.csv to workable format."""
        path = self.variables_path
        with open(path, "r", encoding="utf-8") as file:
            reader = pandas.read_csv(file, header="infer", iterator=True, chunksize=1)
            for line in reader:
                yield (
                    line["study_name"].item(),
                    line["dataset_name"].item(),
                    line["variable_name"].item(),
                )
