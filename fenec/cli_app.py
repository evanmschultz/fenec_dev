import logging
import typer
from typing import Annotated, Literal, Optional, Any
from pathlib import Path
from fenec import Fenec
from fenec.updaters.graph_db_updater import GraphDBUpdater
from rich import print
from fenec.utilities.logger.logging_config import setup_logging

app = typer.Typer()

fenec_instance: Optional[Fenec] = None


def process_codebase(
    fenec_instance: Fenec,
    num_of_passes: int = 3,
    process_all: bool = False,
) -> None:
    """
    Process the codebase at the given path.
    """
    try:
        fenec_instance.process_codebase(num_of_passes, process_all)
        typer.echo("Codebase processing complete.")
    except Exception as e:
        logging.exception("Error processing codebase")
        typer.echo(f"Error processing codebase: {e}")
        raise typer.Exit(1)


def connect_to_vectorstore(fenec_instance: Fenec) -> None:
    """
    Connect to an existing vectorstore.
    """
    try:
        fenec_instance.connect_to_vectorstore()
        typer.echo("Connected to existing vectorstore.")
    except Exception as e:
        logging.exception("Error connecting to vectorstore")
        typer.echo(f"Error connecting to vectorstore: {e}")
        raise typer.Exit(1)


def chat_loop() -> None:
    """
    Start a chat session with Fenec.
    """
    if not fenec_instance:
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
            response = fenec_instance.chat(user_input)
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
    path: Annotated[
        str, typer.Argument(help="The path to the directory containing the codebase")
    ] = ".",
    update: Annotated[
        bool,
        typer.Option(
            help="Whether to update the summaries and databases with the code that has changed since the last git commit"
        ),
    ] = False,
    update_all: Annotated[
        bool,
        typer.Option(
            help="Whether to update the summaries and databases for the whole project, `update` must be False"
        ),
    ] = False,
    chat: Annotated[
        bool,
        typer.Option(
            help="Whether to start a chat session with Fenec, if updating it will run after processing the codebase"
        ),
    ] = True,
    passes: Annotated[
        int,
        typer.Argument(
            help="The number of passes the summarizer will take, 1 is bottom-up, 3 is bottom-up, top-down, then bottom-up again"
        ),
    ] = 3,
) -> None:
    """
    Process the codebase and start a chat session with Fenec.
    """
    setup_logging()

    try:
        resolved_path: Path = Path(path).resolve()

        if passes not in {1, 3}:
            raise typer.BadParameter("Number of passes must be 1 or 3")

        global fenec_instance
        fenec_instance = Fenec(path=resolved_path)

        if update:
            print(
                f"[bold blue]FENEC[/bold blue]\n\nProcessing updated codebase at path: '{resolved_path}'"
            )
            process_codebase(fenec_instance, passes, False)
        elif update_all:
            print(
                f"[bold blue]FENEC[/bold blue]\n\nProcessing the entire codebase at path: '{resolved_path}'"
            )
            process_codebase(fenec_instance, passes, True)
        else:
            print("[blue]FENEC[/blue]\n\nConnecting to existing vectorstore")
            connect_to_vectorstore(fenec_instance)
        if chat:
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
