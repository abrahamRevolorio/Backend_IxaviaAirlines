from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware

async def security_headers(request: Request, call_next) -> Response:
    
    response = await call_next(request)

    response.headers.update({
        "x-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=()"
    })

    return response

def setup_cors(app):
    #Llamamos al los metodos de seguridad
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )
