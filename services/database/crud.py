from .database import async_engine
from .models import *
from sqlalchemy import select, update, insert, delete
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DBAPIError
import asyncio


def db_connection(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                try:                
                    result = await func(session, *args, **kwargs)
    
                    return result
                except OSError:
                    return {"status": "error", "error": "DB connection in the server does not work, maybe the container is not running"}
                except Exception as e:
                    print("An error occurred:", e)
                    raise
    return wrapper

@db_connection
async def get_email_by_ids(session: AsyncSession, lists_ids: list):
    list_emails = []

    for user_id in lists_ids:
        result = await session.execute(select(User).where(User.id == user_id))
        user_email = result.scalar_one_or_none()
        if user_email:
            list_emails.append(user_email.email)

    return list_emails

async def main_testing():
    user_id = "53f22083-76f4-43fd-ad6d-d35de69791ee"
    result = await get_email_by_ids([user_id])
    print(result)

if __name__ == "__main__":
    asyncio.run(main_testing())