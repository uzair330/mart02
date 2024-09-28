from sqlmodel import Field, SQLModel
from uuid import uuid4, UUID
from datetime import datetime, timezone




class TimestampMixin(SQLModel):
    created_at:datetime=Field(default=datetime.now(timezone.utc))
    updated_at: datetime=Field(default_factory=lambda:datetime.now(timezone.utc))

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    username: str
    password: str

class User(UserBase,TimestampMixin, table=True):
    id:UUID | None =Field(primary_key=True, index=True ,default_factory = uuid4)
    iss_key: str = Field (default_factory=lambda: uuid4().hex)
    is_verified: bool = Field(default=False)

class UpdatingUser(SQLModel):
    username: str | None
    email :str | None
    