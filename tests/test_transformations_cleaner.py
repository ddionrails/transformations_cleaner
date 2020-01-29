import tempfile
import typing
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from networkx import DiGraph

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


class TestInput(unittest.TestCase):

    tmp_transformations: typing.IO
    tmp_variables: typing.IO

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

    def setUp(self):
        self.tmp_transformations: typing.IO = tempfile.NamedTemporaryFile()
        self.tmp_transformations.write(bytes(TRANSFORMATIONS))
        self.tmp_transformations.seek(0)

        self.tmp_variables = tempfile.NamedTemporaryFile()
        self.tmp_variables.write(bytes(VARIABLES))
        self.tmp_variables.seek(0)

        self.cleaner = Cleaner(
            transformations_path=Path(self.tmp_transformations.name),
            variables_path=Path(self.tmp_variables.name),
            version="v34",
        )

        return super().setUp()

    def test_read_transformations(self):
        reader = self.cleaner.read_transformations()
        result = next(reader)
        expected = {
            "input": ("test-study", "test-dataset", "var1"),
            "output": ("test-study", "test-dataset", "var2"),
        }
        self.assertSequenceEqual(expected, result)
        filtered = {
            "input": ("test-study", "test-dataset", "var5"),
            "output": ("test-study", "test-dataset", "var6"),
        }
        self.assertNotIn(filtered, list(reader))

    def test_read_variables(self):
        reader = self.cleaner.read_variables()
        result = next(reader)
        self.assertTupleEqual(("test-study", "test-dataset", "var1"), result)
        result = next(reader)
        self.assertTupleEqual(("test-study", "test-dataset", "var2"), result)

    @patch(
        "transformations_cleaner.transformations_cleaner.Cleaner.read_transformations",
        new_callable=MagicMock,
    )
    def test_get_graph(self, mocked_read: MagicMock):
        mocked_read.return_value = self.mocked_relations
        path = "/test/test.csv"
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

    def tearDown(self):
        self.tmp_transformations.close()
        return super().tearDown()
