import sys
sys.path.append("..")

import models
from database import engine
from pydantic import BaseModel
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from .auth import get_current_user, verify_password, get_password_hash
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found."}}
)
models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")


def get_db():
    """Creates a DB session."""
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        print("Database error:", e)
    finally:
        db.close()


db_dependency = Session, Depends(get_db)
user_dependency = dict, Depends(get_current_user)
http_exception_401 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate user."
)


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str


@router.get(path="/edit-password", response_class=HTMLResponse)
async def edit_user_view(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(
            url="/auth",
            status_code=status.HTTP_302_FOUND
        )
    return templates.TemplateResponse(
        name="edit-user-password.html",
        context={
            "request": request,
            "user": user
        }
    )


@router.post("/edit-password", response_class=HTMLResponse)
async def user_password_change(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    user_data = db.query(models.Users).filter(
        models.Users.username == username
    ).first()
    msg = "Invalid username or password."
    if user_data is not None:
        if username == user_data.username and verify_password(
            plain_password=password,
            hashed_password=user_data.hashed_password
        ):
            user_data.hashed_password = get_password_hash(password2)
            db.add(user_data)
            db.commit()
            msg = "Password has been updated."
    return templates.TemplateResponse(
        name="edit-user-password.html",
        context={
            "request": request,
            "user": user,
            "msg": msg
        }
    )
