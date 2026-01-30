from fastapi import FastAPI

from src.routes import utils, users, items


app = FastAPI()

app.include_router(utils.router)
app.include_router(users.router)
app.include_router(items.router)
