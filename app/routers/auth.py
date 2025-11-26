from fastapi import APIRouter
from fastapi.responses import HTMLResponse

auth_router = APIRouter()

@auth_router.get("/login", include_in_schema=False)
def login_page():
    return HTMLResponse("<h1>Auth OK</h1>")
