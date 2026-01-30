import typer

app = typer.Typer(no_args_is_help=True)

@app.command()
def hello() -> None:
    """Sanity check."""
    print("SpecForge is alive.")

if __name__ == "__main__":
    app()
