from fastapi import HTTPException


def not_found(message: str) -> HTTPException:
    return HTTPException(status_code=404, detail=message)


def permission_denied(message: str = "Permission denied.") -> HTTPException:
    return HTTPException(status_code=403, detail=message)


def validation_error(message: str) -> HTTPException:
    return HTTPException(status_code=422, detail=message)


def conflict(message: str) -> HTTPException:
    return HTTPException(status_code=409, detail=message)
