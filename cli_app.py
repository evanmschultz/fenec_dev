import typer
from typing import Optional
from postcode import Postcode
from postcode.updaters.graph_db_updater import GraphDBUpdater

app = typer.Typer()

postcode_instance: Optional[Postcode] = None


def process_codebase(path: str) -> None:
    global postcode_instance
    postcode_instance = Postcode()
    updater = GraphDBUpdater(path)
    postcode_instance.process_entire_codebase(updater)
    typer.echo("Codebase processing complete.")


def chat_loop() -> None:
    global postcode_instance
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
        response = postcode_instance.chat(user_input)
        typer.echo(f"AI: {response}")


@app.command()
def main(
    path: str = typer.Option(".", help="Path to the project directory"),
    process: bool = typer.Option(True, help="Process the codebase before chatting"),
) -> None:
    """
    Process the codebase and start a chat session with Postcode.
    """
    if process:
        typer.echo(f"Processing codebase at {path}...")
        process_codebase(path)

    chat_loop()


if __name__ == "__main__":
    app()
