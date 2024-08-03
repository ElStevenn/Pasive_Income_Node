from .database import async_engine
from .models import *
from sqlalchemy import select, update, insert, delete, join
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DBAPIError
from fastapi import HTTPException
from typing import List, Literal, Optional
import asyncio
import numpy as np
import datetime, uuid


def db_connection(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                try:                
                    result = await func(session, *args, **kwargs)
    
                    return result
                except OSError:
                    return {"status": "error", "error": "DB connection in the server does not work, maybe the container is not running or IP is wrong since you've restarted the node"}
                except Exception as e:
                    print("An error occurred:", e)
                    raise
    return wrapper

@db_connection
async def get_email_by_ids(session: AsyncSession, lists_ids: List[str]):
    list_emails = []

    for user_id in lists_ids:
        result = await session.execute(select(User).where(User.id == user_id))
        user_email = result.scalar_one_or_none()
        if user_email:
            list_emails.append(user_email.email)

    return list_emails


@db_connection
async def add_new_alerts(session: AsyncSession, alert_id: uuid.UUID,  user_ids: List[str], alert_execution: datetime.datetime, message: str, headline: Optional[str] = None, alert_type: Literal["normal", "advise", "recommendation", "alert", "notification"] = "normal"):
    for user_id in user_ids:
        new_alert = Alert(
            id=alert_id,
            user_id = user_id,
            execution_alert_datetime = alert_execution,
            type = alert_type,
            headline = headline,
            message = message
        )
        session.add(new_alert)
        await session.flush()
    

@db_connection
async def get_alerts(session: AsyncSession, alert_id: str):
    result = await session.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    
    return alert

@db_connection
async def delete_alert(session: AsyncSession, alert_id: str):
    result = await session.execute(delete(Alert).where(Alert.id == alert_id))
    deleted_alert = result.scalar_one_or_none()

    if deleted_alert:
        return {"status": "sucess", "response": f"Alert {alert_id} deleted"}
    else:
        return {"status": "error", "response": f"Alert {alert_id} doesn't exsit"}

@db_connection
async def fear_greed_add_new_subscriber(session: AsyncSession, user_id: uuid.UUID, level: Literal[1, 2, 3]):
    """Add new subscriber to fear and greed index"""
    res = await session.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} does not exist"
        )

    res = await session.execute(select(Fear_greed_bot).where(Fear_greed_bot.user_id == user_id))
    subscriber = res.scalar_one_or_none()

    if subscriber:
        await session.execute(update(Fear_greed_bot).where(Fear_greed_bot.user_id == user_id).values(level=level))
        return {"status": "success", "response": f"Level updated to {level}"}
    else:
        new_subscriber = Fear_greed_bot(
            user_id=user_id,
            level=level
        )

        session.add(new_subscriber)
        await session.flush()

        return {"status": "success", "response": "new user added successfully!"}


@db_connection
async def fear_greed_delete_subscriber(session: AsyncSession, user_id: uuid.UUID):
    """Delete a subscriber of fear and greed bot"""
    result = await session.execute(delete(Fear_greed_bot).where(Fear_greed_bot.user_id == user_id))
    await session.flush()

    if result.rowcount > 0:
        return {"status": "success", "response": f"User {user_id} has been deleted"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} does not exist"
        )

@db_connection
async def get_users_list(session: AsyncSession, level: int):
    """Get all the user emails from the list"""
    result = await session.execute(
        select(User.email)
        .join(Fear_greed_bot, Fear_greed_bot.user_id == User.id)
        .where(Fear_greed_bot.level == level)
    )
    
    users = np.array([user[0] for user in result.all()])

    return users

async def main_testing():
    user_id = "53f22083-76f4-43fd-ad6d-d35de69791ee"
    result = await get_users_list(1)
    print(result)

if __name__ == "__main__":
    asyncio.run(main_testing())