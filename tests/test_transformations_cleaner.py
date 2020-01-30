"""All unittests for the package."""
import tempfile
import typing
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from networkx import DiGraph
from typer.testing import CliRunner

from transformations_cleaner.__main__ import CLI
from transformations_cleaner.transformations_cleaner import Cleaner

TRANSFORMATIONS = (
    (
        b"input_study,input_dataset,input_version,input_variable,"
        b"output_study,output_dataset,output_version,output_variable"
    )
    + b"""
test-study,test-dataset,v32,var1,test-study,test-dataset,v34,var2
test-study,test-dataset,v32,var1,test-study,test-dataset,v34,var3
test-study,test-dataset,v32,var2,test-study,test-dataset,v34,var4
test-study,test-dataset,v32,var3,test-study,test-dataset,v34,var5
test-study,test-dataset,v32,var5,test-study,test-dataset,v33,var6
test-study,test-dataset,v32,var10,test-study,test-dataset,v34,var11
test-study,test-dataset,v32,var11,test-study,test-dataset,v34,var12
"""
)

VARIABLES = (
    (b"study_name,dataset_name,variable_name,concept_name,source,item_id,ID")
    + b"""
test-study,test-dataset,var1,some-concept,v34,5323,test-dataset|var1
test-study,test-dataset,var2,some-concept,v34,5533,test-dataset|var2
test-study,test-dataset,var3,some-concept,v34,6734,test-dataset|var3
test-study,test-dataset,var10,some-concept,v34,7576,test-dataset|var10
test-study,test-dataset,var11,some-concept,v34,6345,test-dataset|var11
"""
)


class TestCleaner(unittest.TestCase):
    """ Test cleaner class functionality."""

    tmp_transformations: typing.IO[bytes]
    tmp_variables: typing.IO[bytes]

    mocked_relations = [
        {
            "input": ("test-study", "test-dataset", "var1"),
            "output": ("test-study", "test-dataset", "var2"),
        },
        {
            "input": ("test-study", "test-dataset", "var2"),
            "output": ("test-study", "test-dataset", "var3"),
        },
    ]

    def setUp(self) -> None:
        self.tmp_transformations = tempfile.NamedTemporaryFile()
        self.tmp_transformations.write(bytes(TRANSFORMATIONS))
        self.tmp_transformations.seek(0)

        self.tmp_variables = tempfile.NamedTemporaryFile()
        self.tmp_variables.write(bytes(VARIABLES))
        self.tmp_variables.seek(0)

        self.cleaner = Cleaner(
            generations_path=Path(self.tmp_transformations.name),
            variables_path=Path(self.tmp_variables.name),
            version="v34",
        )

        return super().setUp()

    def test_read_transformations(self) -> None:
        """Reader should filter variables and return only selected fields.

        Filtering should be dependent on version passed to Cleaner instance.
        """
        reader = self.cleaner.read_transformations()
        result = next(reader)
        expected = {
            "input": ("test-study", "test-dataset", "var1"),
            "output": ("test-study", "test-dataset", "var2"),
        }
        self.assertDictEqual(expected, result)

    def test_filter_variables(self) -> None:
        """Intermediate Variables should be filtered out by this function.

        Intermediate Variables are those, that are of the wrong version
        or that are not found in the variables.csv
        """
        graph = self.cleaner.get_graph()
        expected = ("test-study", "test-dataset", "var6")
        self.assertIn(expected, graph)
        result = self.cleaner.filter_variables()
        self.assertNotIn(expected, result)

    def test_read_variables(self) -> None:
        """Should give a similar output as the transformations reader."""
        reader = self.cleaner.read_variables()
        result = next(reader)
        self.assertTupleEqual(("test-study", "test-dataset", "var1"), result)
        result = next(reader)
        self.assertTupleEqual(("test-study", "test-dataset", "var2"), result)

    @patch(
        "transformations_cleaner.transformations_cleaner.Cleaner.read_transformations",
        new_callable=MagicMock,
    )
    def test_get_graph(self, mocked_read: MagicMock) -> None:
        """Relationships should be loaded, transitive relations added."""
        mocked_read.return_value = self.mocked_relations
        graph = self.cleaner.get_graph()
        self.assertIsInstance(graph, DiGraph)
        mocked_read.assert_called()
        self.assertIn(self.mocked_relations[0]["input"], graph)
        self.assertIn(
            ("test-study", "test-dataset", "var2"),
            graph[self.mocked_relations[0]["input"]],
        )
        self.assertIn(
            ("test-study", "test-dataset", "var3"),
            graph[self.mocked_relations[0]["input"]],
        )

    def tearDown(self) -> None:
        self.tmp_transformations.close()
        return super().tearDown()


class TestCLI(unittest.TestCase):
    """Test for the cli."""

    def test_cli(self) -> None:
        """Does the cli take the desired options?"""
        runner = CliRunner()
        result = runner.invoke(CLI, ["--help"])

        self.assertIn("Create a cleaned up transformations file.", result.output)
        result = runner.invoke(CLI, ["v34"])
        result = runner.invoke(
            CLI,
            [
                "v34",
                "--generations-file",
                "./test/gen.csv",
                "--variables-file",
                "./test/var.csv",
                "--transformations-path",
                "./test_out/",
            ],
        )
