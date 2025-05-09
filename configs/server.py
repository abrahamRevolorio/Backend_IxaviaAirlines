from fastapi import FastAPI, Request
from middlewares.security import security_headers, setup_cors
from middlewares.limiter import limiter

app = FastAPI()

setup_cors(app)
app.middleware("http")(security_headers)
app.middleware("https")(security_headers)
app.state.limiter = limiter

@app.get("/")
@limiter.limit("5/minute")
async def home(request: Request):
    return {"message": "Funciona El Server Wey!"}
