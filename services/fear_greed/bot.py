import json, sys, os, asyncio
import numpy as np
import datetime, aiohttp
from openai import AsyncOpenAI
from fastapi import HTTPException

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from services.fear_greed.fear_greed_bot import Fear_Greed_Index
from services.database import crud

"""



"""


fear_and_greed_service = Fear_Greed_Index()
openai = AsyncOpenAI()


async def write_email(messages, level: int):
    prompt = "Summarize the provided array content for an email about crypto investment advice. The importance levels are: level 1 (low importance), level 2 (medium importance), and level 3 (high importance - write this part as best as you can). Provide a JSON with a subject, headline and a description"
    joined_messages = " | ".join(messages)
    model = "gpt-4"

    response = await openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt + " to output JSON."},
            {"role": "user", "content": joined_messages},
            {"role": "user", "content": f"Fear and Greed acutal value is: {fear_and_greed_service.get_FnG()}"},
            {"role": "user", "content": f"Level of importance: {level}"}
        ]
    )

    response_content = response.choices[0].message.content
    email_data = json.loads(response_content)

    return {
        "headline": email_data.get("headline"),
        "subject": email_data.get("subject"),
        "description": email_data.get("description")
    }


async def fear_greed_job():
    if await fear_and_greed_service.conf_status() == "stopped":
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to execute this, since the status is stopped.",
            headers={"X-Error": "Operation not allowed when status is stopped"}
        )

    notifications1, notifications2, notifications3 = await fear_and_greed_service.should_notify()
    today = datetime.datetime.now().strftime("%d/%m/%Y")

    # GROUP 1 (Everyday notification)
    if not notifications2 and not notifications3:
        g1_notifications = np.hstack((notifications1, notifications2, notifications3))
        response1 = await write_email(g1_notifications, 1)

        # Addapt responses
        try:
            response1["subject"] = f"{response1["subject"].split(":")[1]} - {today}"
        except IndexError:
            response1["subject"] = f"{response1["subject"]} - {today}"
        response1["headline"] = response1["headline"] + " - Notification with low importance" 

        # Get users with this subscription 1
        user_emails = await crud.get_users_list('1')
        
        # Send emails to all user subscribed
        if user_emails:
            asyncio.gather(*[send_email(user, response1["subject"], response1["headline"], response1["description"], ["https://alternative.me/crypto/fear-and-greed-index.png"]) for user in user_emails])

    # GROUP 2
    elif not notifications2:
        g2_notificatios = np.hstack((notifications2, notifications3))
        if np.any(g2_notificatios):
            response2 = await write_email(g2_notificatios, 2)

            # Adapt responses
            try:
                response2["subject"] = f"{response2["subject"].split(":")[1]} - {today}"
            except IndexError:
                response2["subject"] = f"{response2["subject"]} - {today}"
            response2["headline"] = response2["headline"] + f" - Notification with medium importance"  

            # Get user with subscription 1 and 2
            user_emails = np.hstack((await crud.get_email_by_ids(1), await crud.get_email_by_ids(2), await crud.get_email_by_ids(2)))

            # Send emails with users subscribed
            asyncio.gather(*[send_email(user, response2["subject"], response2["headline"], response2["description"], ["https://alternative.me/crypto/fear-and-greed-index.png"]) for user in user_emails])


    # GROUP 3
    else:
        g3_notifications = notifications3
        if np.any(g3_notifications):
            response3 = await write_email(g3_notifications, 3)

            # Adapt responses
            try:
                response3["subject"] = f"{response3["subject"].split(":")[1]} - {today}"
            except IndexError:
                response3["subject"] = f"{response3["subject"]} - {today}"
            response3["headline"] = response3["headline"] + f" - Notification with medium importance"  

            # Get user with subscription 1, 2 and 3
            user_emails = np.hstack((await crud.get_email_by_ids(1), await crud.get_email_by_ids(2), await crud.get_email_by_ids(1)))

            # Send email with users subscribed
            asyncio.gather(*[send_email(user, response3["subject"], response3["headline"], response3["description"], ["https://alternative.me/crypto/fear-and-greed-index.png"]) for user in user_emails])


async def send_email(receiver_email, subject, headline, text, images: list):
    url = "http://18.227.161.231:8000/send_email"
    data = {
        "receiver_email": receiver_email,
        "subject": subject,
        "type": "recommendation",
        "message": {
            "crypto_name": "FEAR AND GREED",
            "headline": headline,
            "subtitle": text,
            "details": "",
            "images_url": images
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data) as response:
            result = await response.json()
            print(result)


async def main_testing():
    await send_email("paumat17@gmail.com", "lolol subject", "LOLOL HEADLINE", "Hey this is the text or before called as subtitle!", ["https://alternative.me/crypto/fear-and-greed-index.png"])


if __name__ == "__main__":

    asyncio.run(fear_greed_job())