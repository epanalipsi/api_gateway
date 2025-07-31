import typer
import async_typer

app = async_typer.AsyncTyper(pretty_exceptions_enable=False)

@app.command()
async def foreground():
    pass

if __name__ == "__main__":
    app()