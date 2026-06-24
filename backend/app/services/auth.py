from datetime import datetime, timedelta
from typing import Optional
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserRole
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(db: AsyncSession, token: str) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    return result.scalar_one_or_none()

DEMO_USERS = [
    {"email": "pm@spectwin.dev", "name": "Alex Chen", "password": "demo1234", "role": UserRole.product_manager},
    {"email": "eng@spectwin.dev", "name": "Jordan Lee", "password": "demo1234", "role": UserRole.engineer},
    {"email": "qa@spectwin.dev", "name": "Morgan Davis", "password": "demo1234", "role": UserRole.qa_lead},
    {"email": "mgr@spectwin.dev", "name": "Riley Kim", "password": "demo1234", "role": UserRole.engineering_manager},
    {"email": "admin@spectwin.dev", "name": "Taylor Park", "password": "demo1234", "role": UserRole.admin},
]

async def seed_demo_users(db: AsyncSession):
    for u in DEMO_USERS:
        result = await db.execute(select(User).where(User.email == u["email"]))
        existing = result.scalar_one_or_none()
        if not existing:
            user = User(
                email=u["email"],
                name=u["name"],
                hashed_password=hash_password(u["password"]),
                role=u["role"]
            )
            db.add(user)
    await db.commit()
