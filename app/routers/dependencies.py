from fastapi import Request, Depends, HTTPException
from typing import Annotated
from app.core import get_async_uow_session, UnitOfWork
from app.models import User


async def get_current_user(
    request: Request,
    uow_session: Annotated[UnitOfWork, Depends(get_async_uow_session)],
):
    payload = getattr(request, "jwt_payload", None)
    if payload is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id: int = int(payload.get("user_id"))
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user: User = await uow_session.auth.find_one_or_none_by_id(user_id=user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    return user
