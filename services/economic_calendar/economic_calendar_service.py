import numpy as np
import pandas as pd
import aiohttp, asyncio, aiofiles
import datetime, sys, os, json, re
from functools import wraps
from investpy import economic_calendar, get_index_countries

def metadata_handle(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_metadata = os.path.join(script_dir, 'metadata.json')

        if not file_metadata:
            raise FileNotFoundError("File 'metadata.json' does not exsit! Create it please")

        async with aiofiles.open(file_metadata, mode='r') as session:
            content = await session.read()
            metadata_file = json.loads(content)
        
        result = await func(self, metadata_file, *args, **kwargs)

        async with aiofiles.open(file_metadata, mode='w') as session:
            await session.write(result)
        
        return result
    return wrapper


class EconomicCalendarData():
    def __init__(self):
        self._script_dir = os.path.dirname(os.path.abspath(__file__))
        self._conf_file = os.path.join(self._script_dir, 'important_events.json')

        if not self._conf_file:
            raise FileNotFoundError("File 'important_events.json' does not exsit! Create it please")

    @metadata_handle
    async def add_new_event_to_triger(self, metadata_file):
        pass
    
    @property
    def important_events(self):
        return json.loads(open(self._conf_file).read())

    async def dialy_job(self):
        df_today = economic_calendar()
        important_events = [important_event['keyword'] for important_event in self.important_events['important_events']]

        importance_events = df_today[df_today['importance'] == 'high']
        
        print(important_events)

async def main():
    economic_calendar = EconomicCalendarData()
    await economic_calendar.dialy_job()


if __name__ == "__main__":
    asyncio.run(main())