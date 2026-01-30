from fastapi import FastAPI

from routes import utils


app = FastAPI()

app.include_router(utils.router)
