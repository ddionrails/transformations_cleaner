"""Everything for cli usage."""

from pathlib import Path

import typer

CLI = typer.Typer()

HELP_TEXT = """Create a cleaned up transformations file.

Loads the relations between variables from a GENERATIONS_FILE.
Relations are expanded with explicit relations between variables that are
only implicitly related in the generations file. (transitive closure)

Variable nodes are then filtered by variables, that exist in the VARIABLES_FILE
and by their VERSION.

A transformations.csv is then written into the
TRANSFORMATIONS_PATH folder.
"""


@CLI.command(help=HELP_TEXT)  # type: ignore
def main(
    version: str,
    generations_file: Path = Path("./metadata/generations.csv"),
    variables_file: Path = Path("./metadata/variables.csv"),
    transformations_path: Path = Path("./ddionrails"),
) -> None:
    """Create a cleaned up transformations file.

    Args:
        generations_file: Path to the generations.csv file.
        variables_file: Path to the variables.csv.
        version: Only relations to variables with this version will be included
                 in the output file.
    """
    typer.echo(generations_file, variables_file, version, transformations_path)
