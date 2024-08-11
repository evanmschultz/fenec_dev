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


def process_codebase(path: Path) -> None:
    """
    Process the codebase at the given path.
    """
    global postcode_instance
    try:
        postcode_instance = Postcode()
        updater = GraphDBUpdater(str(path))
        postcode_instance.process_entire_codebase(updater)
        typer.echo("Codebase processing complete.")
    except Exception as e:
        logging.exception("Error processing codebase")
        typer.echo(f"Error processing codebase: {e}")
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

    typer.echo("Chat mode started. Type 'exit' to quit.")
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

    path = Path(path_str).resolve()
    if not path.exists():
        raise typer.BadParameter(f"The path '{path}' does not exist.")
    return path


@app.command()
def main(
    path: Any = typer.Option(
        ".",
        help="Path to the project directory",
    ),
    process: bool = typer.Option(True, help="Process the codebase before chatting"),
) -> None:
    """
    Process the codebase and start a chat session with Postcode.
    """
    setup_logging()
    try:
        resolved_path = get_path_from_option(path)
        logging.info(f"Starting Postcode with path: {resolved_path}")

        if process:
            print(
                f"[blue]POSTCODE[/blue]\n\nProcessing codebase at path: '{resolved_path}'"
            )
            process_codebase(resolved_path)

        chat_loop()
    except typer.BadParameter as e:
        logging.error(f"Invalid path: {e}")
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
