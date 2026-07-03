from pyrogram import idle
from core.clients import bot,start_saved_sessions,stop_all_user_clients
from core.database import db
from core.scheduler import start_scheduler,scheduler
async def main():
    started=False
    try:
        await db.setup()
        start_scheduler()
        await bot.start();started=True
        await start_saved_sessions()
        print("✅ Swaggy Forwarder started — press Ctrl+C to stop")
        await idle()
    except Exception as e:
        print(f"❌ Startup error: {e}")
    finally:
        print("\n🛑 Shutting down gracefully...")
        await stop_all_user_clients()
        if scheduler.running:scheduler.shutdown(wait=False)
        if started:await bot.stop()
        db.client.close()
        print("✅ Shutdown complete")
if __name__=="__main__":
    bot.run(main())
