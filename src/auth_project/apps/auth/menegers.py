from fastapi import Depends, HTTPException
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from src.auth_project.apps.auth.schemas import CreateUser, UserReturnData
from src.auth_project.core.core_dependency.db_dependency import DBDependency
from src.auth_project.database.models.user import User


class UserManager:
    def __init__(self, model: type[User], db: DBDependency = Depends(DBDependency)) -> None:
        self.model = model
        self.db = db

    async def create_user(self, user: CreateUser) -> UserReturnData:
        async with self.db.db_session() as session:
            query = insert(self.model).values(**user.model_dump()).returning(self.model)

            try:
                result = await session.execute(query)
            except IntegrityError:
                raise HTTPException(status_code=400, detail="User already exists")

            await session.commit()

            user_data = result.scalar_one()

            return UserReturnData(**user_data.__dict__)
