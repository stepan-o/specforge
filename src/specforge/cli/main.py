import typer

app = typer.Typer(no_args_is_help=True)

@app.callback()
def main() -> None:
    """SpecForge CLI."""
    # This keeps Typer in "group" mode (subcommands enabled).
    pass

@app.command()
def hello() -> None:
    """Sanity check."""
    print("SpecForge is alive.")
