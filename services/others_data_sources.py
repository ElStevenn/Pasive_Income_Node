import aiohttp
import asyncio
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import boto3, time, os
from dotenv import load_dotenv
load_dotenv()

class Other_Data_Sources:
    def __init__(self):
        self.url_fear_greed = 'https://api.alternative.me/fng/?limit=2'
        self.url_crypto_volatility_index = "https://www.investing.com/indices/crypto-volatility-index"
        self.url_bitcoin_dominance = ""
        self.client_s3 = boto3.client('s3', 
                         region_name='us-east-1',
                         aws_access_key_id=os.getenv('AWS_ACCES_KEY'), 
                         aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))

    async def get_today_fear_greed(self) -> tuple:
        """Get today's fear greed based on the Alternative.me page"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url_fear_greed) as response:
                content = await response.json()
                value = content['data'][0]['value']
                value_classification = content['data'][0]['value_classification']
        return value, value_classification

    async def get_crypto_volatility_index(self):
        """Get volatility Index"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url_crypto_volatility_index) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'lxml')
                div_min = soup.find('div', class_='min-w-0')
                price_div = div_min.find('div', class_='text-5xl/9 font-bold text-[#232526] md:text-[42px] md:leading-[60px]')
                return price_div.text


    def get_historical_CVI(self, interval: str = "1H", lookback_minutes: int = 1440):
            cvi_dataset = self.get_CVI_dataset()
            granularity_map = {
                '1m': '1T',
                '5m': '5T',
                '15m': '15T',
                '30m': '30T',
                '1h': '1H',
                '4h': '4H',
                '1d': '1D',
                '1w': '1W'  
            }

            if interval not in granularity_map:
                raise ValueError(f"Unsupported interval: {interval}")

            resample_interval = granularity_map[interval]
            lookback_seconds = lookback_minutes * 60

            cvi_dataset['Timestamp'] = pd.to_datetime(cvi_dataset['Timestamp'])
            end_time = pd.Timestamp.now()
            start_time = end_time - pd.Timedelta(seconds=lookback_seconds)
            cvi_dataset = cvi_dataset[(cvi_dataset['Timestamp'] >= start_time) & (cvi_dataset['Timestamp'] <= end_time)]
            
            cvi_dataset = cvi_dataset.set_index('Timestamp').resample(resample_interval).mean().reset_index()

            cvi_dataset['Timestamp'] = cvi_dataset['Timestamp'].apply(lambda x: time.mktime(x.timetuple()))
            return cvi_dataset.to_numpy()
    
    def get_CVI_dataset(self) -> pd.DataFrame:
        """Get CVI Dataset from AWS"""
        try:
            response = self.client_s3.get_object(Bucket='paus-bucket', Key='datasets/CVI_data_collector.csv')
            content = response['Body'].read().decode('utf-8')
            df = pd.read_csv(StringIO(content))
            return df
        except self.client_s3.exceptions.NoSuchKey:
            print("Specified key does not exist")
            return pd.DataFrame(columns=['Timestamp', 'Price'])
        except Exception as ex:
            print(f"An error occurred: {ex}")
            return pd.DataFrame(columns=['Timestamp', 'Price'])
        
    async def get_bitcoin_dominance(self):
        pass    

async def main_testings():
    data_sources = Other_Data_Sources()
    result = data_sources.get_historical_CVI("15m")
    print(result)

if __name__ == "__main__":
    asyncio.run(main_testings())
