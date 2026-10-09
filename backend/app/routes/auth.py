
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import bcrypt
from datetime import datetime, timedelta, timezone
import jwt
from fastapi.security import OAuth2PasswordRequestForm
from app.core.connections import get_pg_connection
from dotenv import load_dotenv
import os


load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES"))

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


@router.post("/register")
def register_user(user: RegisterRequest):

    # Hash the password before storing it.
    # The actual password is never stored in PostgreSQL.
    password_hash = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (
                        username,
                        email,
                        password_hash
                    )
                    VALUES (%s, %s, %s)
                    RETURNING id, username, email, created_at
                    """,
                    (
                        user.username,
                        user.email,
                        password_hash,
                    ),
                )

                row = cursor.fetchone()

            conn.commit()

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists",
        )

    return {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "created_at": row[3],
    }


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):

    username = form_data.username
    password = form_data.password

    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, email, password_hash
                FROM users
                WHERE username = %s
                """,
                (username,),
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    user_id, username, email, password_hash = row

    password_valid = bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_EXPIRATION_MINUTES
    )

    token = jwt.encode(
        {
            "sub": str(user_id),
            "username": username,
            "exp": expiration,
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
