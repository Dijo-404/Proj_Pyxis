from fastapi import HTTPException


def not_found(message: str = "Resource not found") -> HTTPException:
    return HTTPException(status_code=404, detail={"code": "not_found", "message": message})
