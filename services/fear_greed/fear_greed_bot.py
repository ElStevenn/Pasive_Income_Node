import aiohttp, aiofiles, os, sys, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from functools import wraps
from io import BytesIO
import asyncio
import json
from collections import deque
from datetime import datetime, timedelta
from typing import Literal
import numpy as np
import pandas as pd


def handle_conf_file(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'internal_conf.json')

        if not os.path.isfile(config_path):
            raise FileNotFoundError("File internal_conf.json not found! Please create it!")

        async with aiofiles.open(config_path, mode='r') as session:
            content = await session.read()
            conf = json.loads(content)

        result = await func(self, conf, *args, **kwargs)

        async with aiofiles.open(config_path, mode='w') as session:
            await session.write(json.dumps(conf, indent=4))

        return result

    return wrapper


class Fear_Greed_Index:
    def __init__(self):
        self.url = "https://api.alternative.me/fng/"
        self.value_classification = {
            range(0, 20): 'Extreme Fear',
            range(20, 40): 'Fear',
            range(40, 60): 'Neutral',
            range(60, 80): 'Greed',
            range(80, 101): 'Extreme Greed'
        }
        self.last_notified_value = None
        self._server_ip = f"http://{os.system('curl ifconfig.me')}"

    def classify_value(self, value):
        for key in self.value_classification:
            if value in key:
                return self.value_classification[key]
        return 'Unknown'

    async def make_request(self, url, headers=None, params = {}):
        str_headers = "?" + "&".join([f"{key}={value}" for key, value in headers.items()]) if headers else ""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}{str_headers}", json=params) as response:
                return await response.json()

    @handle_conf_file
    async def conf_status(self, conf):
        return conf['status']

    @handle_conf_file
    async def set_conf_status(self, conf, new_conf: str):
        conf['status'] = new_conf

    @handle_conf_file
    async def set_today_analysis(self, conf, today_analysis):
        conf['today_analysis'] = today_analysis

    @handle_conf_file
    async def get_today_analysis(self, conf):
        return conf['today_analysis']

    @handle_conf_file
    async def get_conf_bot_id(self, conf):
        return conf['bot_id']

    @handle_conf_file
    async def set_conf_bot_id(self, conf, bot_id):
        conf['bot_id'] = bot_id

    @handle_conf_file
    async def get_description(self, conf):
        return conf['description']

    def take_screenshot(url, save_path):
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # Set Up and open driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)

        time.sleep(2)

        driver.save_screenshot(save_path)

        driver.quit()

    async def run_fear_and_greed_bot(self):
        try:
            if await self.conf_status() == "running" or await self.get_conf_bot_id():
                return {"status": "Not Modified", "message": "The bot is already running"}
   
            private_url = "http://18.116.72.135:8000/schedule_limited_interval"
            data = {
                "url": self._server_ip + "/fear_greed/run_bot",
                "method": "patch",
                "data": {},
                "headers": {},
                "execute_at": "01:01",
            }

            async with aiohttp.ClientSession() as client:
                async with client.patch(private_url, json=data) as response:
                    result = await response.json()
                    if result['error']:
                        print("Something was wrong while executing the bot")
                        await self.notify_error("Error while executing bot", result['message'])
                        await self.set_conf_bot_id("")
                        return {"status":"error", "message":f"Something was wrong while executing the bot: {result['message']}"}
                    else:
                        await self.set_conf_status("running")
                        await self.set_conf_bot_id(result['task_id'])
                        return {"status":"success", "message":"Sweet, bot is running successfully"}
        except Exception as e:
            return {"status":"error","message": f"You are executting this in a local machine: {e}"}

    async def stop_fear_and_greed_bot(self):
        try:
            if await self.conf_status() == "stopped" or not await self.get_conf_bot_id():
                return {"status": "Not Modified", "message": "The bot is already stopped"}
            task_id = await self.get_conf_bot_id()
            private_url = f"http://18.116.72.135:8000/delete_task/{task_id}"

            async with aiohttp.ClientSession() as client:
                async with client.patch(private_url) as response:
                    result = await response.json()
                    if result['error']:
                        print("Someting was wrong while stopping the FG Bot")
                        await self.notify_error("Error while stopping the bot", result['message'])
                        return {"status":"error","message": f"An error ocurred while stopping the bot: {result['message']}"}
                    else:
                        await self.set_conf_status("stopped")
                        return {"status":"success", "message": "Sweet, bot has stopped successfully"}
        except Exception as e:
            return {"status":"error","message": f"You are executting this in a local machine: {e}"}

    async def restart_fear_and_greed_bot(self):
        pass

    async def status_bot_fear_greed(self):
        try:
            pass

        except:
            return "You are executting this in a local machine!"

    async def get_FnG(self) -> int:
        """Get today's fear and greed index"""
        response = await self.make_request(self.url)
        return int(response['data'][0]['value'])

    async def get_historical_short(self):
        # Get Response
        response = await self.make_request(self.url, headers={"limit": "60"})
        # Build Array
        result_array =  np.array([np.int16(val['value']) for val in response['data']])
        return result_array

    async def get_btc_price(self) -> float:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        response = await self.make_request(url)
        return float(response['bitcoin']['usd'])

    async def get_btc_mean_price_day(self):
        url = "https://api.bitget.com/api/mix/v1/market/candles"
        current_time = int(pd.Timestamp.utcnow().timestamp() * 1000)
        one_day = 24 * 60 * 60 * 1000
        start_time = current_time - 30 * one_day  # 30 days ago
        
        params = {
            'symbol': "BTCUSDT_UMCBL", 
            'productType': "umcbl",
            'granularity': '1D',  # 1-day intervals
            'startTime': start_time,
            'endTime': current_time
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

                # Assuming data is a list of OHLCV data with each entry containing [timestamp, open, high, low, close, volume]
                candles = data
                if candles is None:
                    raise ValueError("Candles data is None")
                
                # Calculate the average price
                prices = [((float(candle[1]) + float(candle[2]) + float(candle[3]) + float(candle[4])) / 4) for candle in candles]
                dates = [pd.to_datetime(int(candle[0]), unit='ms') for candle in candles]
                
                # Creating a DataFrame to calculate the mean price per day
                df = pd.DataFrame({'date': dates, 'price': prices})
                mean_prices = df.groupby(df['date'].dt.date).mean()
                
                return mean_prices['price'].to_numpy()

    async def notify_error(self, error_name, error_description):
        url = "http://18.227.161.231/notificate_node_issue"
        data = {
            "error_type": "bug",
            "description": f"Error name: {error_name} | Description: {error_description}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=data) as response:
                await response.json()


    def detect_trend_break(self, arr):
        messages = []

        # 2 weeks
        weeks2 = arr[1:14 + 1]
        differences_2 = np.diff(weeks2, n=1)
        max_2 = np.max(differences_2) if np.max(differences_2) >= 10 else 10
        min_2 = np.min(differences_2) if np.min(differences_2) <= -10 else -10
        todays_diference = arr[1] - arr[0]

        if todays_diference >= max_2:
            messages.append({"importance": 3, "message": f"The trend has suddenly fallen by {todays_diference} points"})
        elif todays_diference <= min_2:
            messages.append({"importance": 3, "message": f"The trend has suddenly risen by {todays_diference} points"})

        if max_2 < 15 or min_2 > -15:
            max_2 = 16
            min_2 = -16
            if todays_diference >= max_2:
                messages.append({"importance": 2, "message": f"The trend has suddenly fallen by {todays_diference} points"})
            elif todays_diference <= min_2:
                messages.append({"importance": 2, "message": f"The trend has suddenly risen by {todays_diference} points"})
            if max_2 < 20 or min_2 > -20:
                max_2 = 21
                min_2 = -21
                if todays_diference >= max_2:
                    messages.append({"importance": 1, "message": f"The trend has fallen by {todays_diference} points"})
                elif todays_diference <= min_2:
                    messages.append({"importance": 1, "message": f"The trend has risen by {todays_diference} points"})

        # 3 weeks in 2 days in a row
        weeks3 = arr[1:21 + 1]
        differences_3 = np.diff(weeks3, n=2)
        max_3 = np.max(differences_3) if np.max(differences_3) >= 15 else 15
        min_3 = np.min(differences_3) if np.min(differences_3) <= -15 else -15

        if todays_diference >= max_3:
            messages.append({"importance": 3, "message": f"The trend has suddenly fallen by {todays_diference} points"})
        elif todays_diference <= min_3:
            messages.append({"importance": 3, "message": f"The trend has suddenly risen by {todays_diference} points"})

        if max_3 < 20 or min_3 > -20:
            max_3 = 21
            min_3 = -21
            if todays_diference >= max_3:
                messages.append({"importance": 2, "message": f"The trend has suddenly fallen by {todays_diference} points"})
            elif todays_diference <= min_3:
                messages.append({"importance": 2, "message": f"The trend has suddenly risen by {todays_diference} points"})
            if max_3 < 25 or min_3 > -25:
                max_3 = 26
                min_3 = -26
                if todays_diference >= max_3:
                    messages.append({"importance": 1, "message": f"The trend has fallen by {todays_diference} points"})
                elif todays_diference <= min_3:
                    messages.append({"importance": 1, "message": f"The trend has risen by {todays_diference} points"})

        # 4 weeks in 3 days in a row falling or going up
        weeks4 = arr[1:28 + 1]
        differences_4 = np.diff(weeks4, n=3)
        max_4 = np.max(differences_4) if np.max(differences_4) >= 20 else 20
        min_4 = np.min(differences_4) if np.min(differences_4) <= -20 else -20

        if todays_diference >= max_4:
            messages.append({"importance": 3, "message": f"The trend has suddenly fallen by {todays_diference} points"})
        elif todays_diference <= min_4:
            messages.append({"importance": 3, "message": f"The trend has suddenly risen by {todays_diference} points"})

        if max_4 < 25 or min_4 > -25:
            max_4 = 26
            min_4 = -26
            if todays_diference >= max_4:
                messages.append({"importance": 2, "message": f"The trend has suddenly fallen by {todays_diference} points"})
            elif todays_diference <= min_4:
                messages.append({"importance": 2, "message": f"The trend has suddenly risen by {todays_diference} points"})
            if max_4 < 30 or min_4 > -30:
                max_4 = 31
                min_4 = -31
                if todays_diference >= max_4:
                    messages.append({"importance": 1, "message": f"The trend has fallen by {todays_diference} points"})
                elif todays_diference <= min_4:
                    messages.append({"importance": 1, "message": f"The trend has risen by {todays_diference} points"})

        return messages
    

    async def should_notify(self):
        current_value = await self.get_FnG(); print(current_value)
        history = await self.get_historical_short(); print(history)
        mean_btc_price = await self.get_btc_mean_price_day()
        btc_price = await self.get_btc_price()
        messages = []
        importance = 0
        
        # Interval 1, detect variations
        if len(history) > 1:
            previous_value = history[1]
            change = current_value - previous_value
    
            if abs(change) >= 15:
                direction = "dropped" if change < 0 else "increased"
                message = {"importance": 3, "message": f"Fear and Greed has {direction} 15 points. Bitcoin (currently priced at {await self.get_btc_price()}$) is likely to see a {'small increase 📈' if direction == 'dropped' else 'correction 📉'}."}
                messages.append(message)
            elif abs(change) >= 10:
                direction = "dropped" if change < 0 else "increased"
                message = {"importance": 2, "message": f"Fear and Greed has {direction} 10 points, significant market movement, monitor closely."}
                messages.append(message)
        
        # Variation over the last 3-5 days down
        if len(history) >= 7 and np.all(np.diff(history[:7]) < 0):
            message = {"importance": 3, "message": "Fear and Greed have consistently dropped over the past 7 days, indicating severe market fear. This does not necessarily mean that the market will go up, but it does suggest that we are in a persistent state of fear"}
            messages.append(message)
        elif len(history) >= 5 and np.all(np.diff(history[:5]) < 0):
            message = {"importance": 2, "message": "Fear and Greed has consistently dropped over the past 5 days, indicating significant market fear."}
            messages.append(message)
        elif len(history) >= 3 and np.all(np.diff(history[:3]) < 0):
            message = {"importance": 1, "message": "Fear and Greed has consistently dropped over the past 3 days, indicating posible starting market fear."}
            messages.append(message)
        
        # Variation over the last 3-5 days up
        if len(history) >= 7 and np.all(np.diff(history[:7]) > 0):
            message = {"importance": 3, "message": "Fear and Greed has consistently increased over the past 7 days, indicating growing market optimism, be careful"}
            messages.append(message)
        elif len(history) >= 5 and np.all(np.diff(history[:5]) > 0):
            message = {"importance": 2, "message":"Fear and Greed has consistently increased over the past 5 days, some significant market optimism."}
            messages.append(message)
        elif len(history) >= 3 and np.all(np.diff(history[:3]) > 0):
            message = {"importance": 1, "message":"Fear and Greed has consistently increased over the past 3 days, posible growing market optimism."}
            messages.append(message)
            
        
        # Variation over the last 7 - 10 days
        if len(history) >= 10:
            if current_value - np.median(history[3:10]) >= 30:
                message = {"importance": 2, "message": "Fear and Greed has increased 10 points over the last 7-10 days, slight positive sentiment, monitor closely."}
                messages.append(message)
            elif np.median(history[3:10]) - current_value >= 30:
                message = {"importance": 2, "message": "Fear and Greed has dropped 10 points over the last 7-10 days, slight market fear, stay alert"}
                messages.append(message)

        
        # Notify if the index is in an extreme range
        ranges = [
            (0, 13, "Fear and Greed has dropped to 0-13, extreme fear is present, consider buying no matter what.", 3),
            (13, 22, "Fear and Greed has dropped to 13-22, significant market fear, potential buying opportunity.", 2),
            (65, 85, "Fear and Greed is steady in the range of 70-90, high greed, consider taking profits.", 1),
            (85, 100, "Fear and Greed is steady in the range of 90-100, extreme greed, consider selling no matter and even consider to enter in short in some cryptos like solana, bnb among other altcoint.", 3),
        ]

        for low, high, message, new_importance in ranges:
            if low <= current_value <= high:
                messages.append({"importance": new_importance, "message": message})

        
        # Calculate 30-Day Moving Average
        if len(mean_btc_price) >= 30:
            btc_moving_average = np.mean(mean_btc_price[-30:])
            fng_moving_average  = np.mean(history[:30])
            
            if current_value > fng_moving_average and btc_price > btc_moving_average:
                    message = {"importance": 1, "message":"Fear and Greed is currently above the 30-day moving average, potential buying opportunity (mid-long term)"}
                    messages.append(message)
            elif current_value < fng_moving_average and btc_price < btc_moving_average:
                messages.append("Fear and Greed is currently below the 30-day moving average, potential selling opportunity (mid-long term)")
                importance = max(importance, 1)

        # Calculate Standart Deviation
        if len(history) >= 30:
                fng_std_dev = np.std(history[:30])
                btc_std_dev = np.std(mean_btc_price[-30:])
                messages.append({"importance": 1, "message": f"Fear and Greed 30-day standard deviation is {fng_std_dev:.2f}. BTC 30-day standard deviation is {btc_std_dev:.2f}."})
        
        # Calculate trend break up or down
        trending_messages = self.detect_trend_break(history)

        if trending_messages:
            for trend_message in trending_messages:
                messages.append(trend_message)

        messages1 = [message.get('message', '') for message in messages if message.get('importance', -1) == 1]
        messages2 = [message.get('message', '') for message in messages if message.get('importance', -1) == 2]
        messages3 = [message.get('message', '') for message in messages if message.get('importance', -1) == 3]

        return messages1, messages2, messages3






async def main():
    fng = Fear_Greed_Index()
    conf = await fng.set_today_analysis("this is today analysis!")
    print(conf)

if __name__ == "__main__":
    asyncio.run(main())
   
