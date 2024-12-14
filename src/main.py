from fastapi import FastAPI
from web import main_page

app = FastAPI()

app.include_router(main_page.router)
