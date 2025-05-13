from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Cabeceras de seguridad básicas
async def securityHeaders(request: Request, callNext) -> Response:
    response = await callNext(request)
    response.headers.update({
        "x-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=()"
    })
    return response

# Permite llamadas desde cualquier origen (útil en desarrollo)
def setupCors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )
