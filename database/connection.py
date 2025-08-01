from prisma import Prisma
import os
from dotenv import load_dotenv

load_dotenv()

prisma = Prisma()

async def connect_db():
    await prisma.connect()
    print("✅ Connected to database")

async def disconnect_db():
    await prisma.disconnect()
    print("❌ Disconnected from database")