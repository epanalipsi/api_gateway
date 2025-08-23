import typer
import async_typer
from database.mongo_manager import database

app = async_typer.AsyncTyper(pretty_exceptions_enable=False)

@app.async_command()
async def reset_db(
    
):
    pass

if __name__ == "__main__":
    app()