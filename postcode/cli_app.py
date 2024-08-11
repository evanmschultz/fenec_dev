import logging
import typer
from typing import Optional, Any
from pathlib import Path
from postcode import Postcode
from postcode.updaters.graph_db_updater import GraphDBUpdater
from rich import print
from postcode.utilities.logger.logging_config import setup_logging

app = typer.Typer()

postcode_instance: Optional[Postcode] = None


def process_codebase(
    path: Path,
    postcode_instance: Postcode,
    num_of_passes: int = 3,
    process_all: bool = False,
) -> None:
    """
    Process the codebase at the given path.
    """
    try:
        updater = GraphDBUpdater(str(path))
        postcode_instance.process_codebase(updater, num_of_passes, process_all)
        typer.echo("Codebase processing complete.")
    except Exception as e:
        logging.exception("Error processing codebase")
        typer.echo(f"Error processing codebase: {e}")
        raise typer.Exit(1)


def connect_to_vectorstore(postcode_instance: Postcode) -> None:
    """
    Connect to an existing vectorstore.
    """
    try:
        postcode_instance.connect_to_vectorstore()
        typer.echo("Connected to existing vectorstore.")
    except Exception as e:
        logging.exception("Error connecting to vectorstore")
        typer.echo(f"Error connecting to vectorstore: {e}")
        raise typer.Exit(1)


def chat_loop() -> None:
    """
    Start a chat session with Postcode.
    """
    if not postcode_instance:
        typer.echo(
            "Error: Codebase has not been processed. Please process the codebase first."
        )
        raise typer.Exit(1)

    print(
        "[blue]Chat[/blue] session started. Type [magenta]'exit'[/magenta] to end the chat."
    )
    while True:
        user_input = typer.prompt("You")
        if user_input.lower() == "exit":
            break
        try:
            response = postcode_instance.chat(user_input)
            typer.echo(f"AI: {response}")
        except Exception as e:
            logging.exception("Error during chat")
            typer.echo(f"Error during chat: {e}")
            break


def get_path_from_option(option_value: Any) -> Path:
    if hasattr(option_value, "default"):
        # If it's an OptionInfo object, use its default value
        path_str = str(option_value.default)
    else:
        # Otherwise, assume it's already a string
        path_str = str(option_value)

    path: Path = Path(path_str).resolve()
    if not path.exists():
        raise typer.BadParameter(f"The path '{path}' does not exist.")
    return path


@app.command()
def main(
    path: str = ".",
    process: bool = False,
    all: bool = False,
    passes: int = 3,
) -> None:
    """
    Process the codebase and start a chat session with Postcode.
    """
    setup_logging()

    try:
        resolved_path: Path = Path(path).resolve()

        if passes not in {1, 3}:
            raise typer.BadParameter("Number of passes must be 1 or 3")

        global postcode_instance
        postcode_instance = Postcode()

        if process:
            print(
                f"[bold blue]POSTCODE[/bold blue]\n\nProcessing codebase at path: '{resolved_path}'"
            )
            process_codebase(resolved_path, postcode_instance, passes, all)
        else:
            print("[blue]POSTCODE[/blue]\n\nConnecting to existing vectorstore")
            connect_to_vectorstore(postcode_instance)

        chat_loop()
    except typer.BadParameter as e:
        logging.error(f"Invalid parameter: {e}")
        typer.echo(str(e))
        raise typer.Exit(1)
    except typer.Exit:
        logging.error("Codebase processing failed")
        raise
    except Exception as e:
        logging.exception("An unexpected error occurred")
        typer.echo(f"An unexpected error occurred: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
