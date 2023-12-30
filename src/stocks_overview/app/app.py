import typer

app = typer.Typer()


@app.command()
def show_stocks() -> None:
    print("showing stocks")


if __name__ == "__main__":
    app()
