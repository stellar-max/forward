import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler=AsyncIOScheduler(timezone="Asia/Kolkata")
def start_scheduler():
    if not scheduler.running:scheduler.start()
async def sleep_delay(seconds):
    if seconds and seconds>0:await asyncio.sleep(min(int(seconds),86400))
