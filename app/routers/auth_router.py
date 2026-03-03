from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.dependencies import get_auth_service
from app.exceptions import UserAlreadyExists, InactiveUser, InvalidCredentials
from app.utils import OAuth2PasswordBearerWithCookie
from app.schemas import User, SUserRegister
from app.core import get_async_uow_session, UnitOfWork
from app.services import AuthService

# pylint: disable=invalid-name
templates = Jinja2Templates(directory="app/templates")

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    uow_session: UnitOfWork = Depends(get_async_uow_session),
):
    user = await uow_session.auth.get_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=401, detail="Inactive user")
    return current_user


@auth_router.post("/token", response_class=HTMLResponse)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    uow_session: UnitOfWork = Depends(get_async_uow_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = await auth_service.login(
            username=form_data.username,
            password=form_data.password,
            uow_session=uow_session,
        )
    except InvalidCredentials:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Incorrect username or password"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except InactiveUser:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Inactive user"},
            status_code=400,
        )

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token", value=f"Bearer {form_data.username}", httponly=True
    )
    return response


@auth_router.get("/logout")
async def login(
    current_user: Annotated[User, Depends(get_current_active_user)],
    uow_session: UnitOfWork = Depends(get_async_uow_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.logout(username=current_user.name, uow_session=uow_session)

    response = RedirectResponse("/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response


@auth_router.get("/login", status_code=status.HTTP_200_OK)
async def get_home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@auth_router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@auth_router.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@auth_router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    uow_session: UnitOfWork = Depends(get_async_uow_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        await auth_service.register(
            username=username, password=password, uow_session=uow_session
        )
    except UserAlreadyExists:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Username already registered"},
            status_code=400,
        )

    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: SUserRegister,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    await auth_service.register_user(user_data)
    return {"message": "Вы успешно зарегистрированы!"}