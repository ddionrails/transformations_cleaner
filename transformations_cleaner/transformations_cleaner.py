from pathlib import Path

import pandas
from networkx import DiGraph
from networkx.algorithms import transitive_closure


class Cleaner:

    graph: DiGraph
    transformations_path: Path
    version: str

    def __init__(self, transformations_path, variables_path, version):
        self.transformations_path = transformations_path
        self.variables_path = variables_path
        self.version = version
        self.graph = self.get_graph()
        super().__init__()

    def get_graph(self):
        transformations = self.read_transformations()
        graph = DiGraph()

        for relation in transformations:
            graph.add_edge(relation["input"], relation["output"])

        return transitive_closure(graph)

    def read_transformations(self):
        path = self.transformations_path
        with open(path, "r", encoding="utf-8") as file:
            reader = pandas.read_csv(file, header="infer", iterator=True, chunksize=1)
            for line in reader:
                if line["output_version"].item() == self.version:
                    yield {
                        "input": (
                            line["input_study"].item(),
                            line["input_dataset"].item(),
                            line["input_variable"].item(),
                        ),
                        "output": (
                            line["output_study"].item(),
                            line["output_dataset"].item(),
                            line["output_variable"].item(),
                        ),
                    }

    def read_variables(self):
        path = self.variables_path
        with open(path, "r", encoding="utf-8") as file:
            reader = pandas.read_csv(file, header="infer", iterator=True, chunksize=1)
            for line in reader:
                yield (
                    line["study_name"].item(),
                    line["dataset_name"].item(),
                    line["variable_name"].item(),
                )

