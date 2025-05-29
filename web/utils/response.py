

from fastapi.responses import JSONResponse
from typing import Any

def success_response(data: Any, status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={
        "status": "success",
        "data": data
    })

def error_response(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={
        "status": "error",
        "message": message
    })