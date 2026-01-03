"""Add stored_filename column to documents table."""
import asyncio
from sqlalchemy import text
from app.db import async_engine

async def add_column():
    async with async_engine.begin() as conn:
        await conn.execute(text(
            "ALTER TABLE documents ADD COLUMN IF NOT EXISTS stored_filename VARCHAR(500)"
        ))
    print("✅ Column 'stored_filename' added successfully!")

if __name__ == "__main__":
    asyncio.run(add_column())
