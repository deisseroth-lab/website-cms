from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URI = "sqlite+aiosqlite:///test.sqlite"

engine = create_async_engine("sqlite+aiosqlite:///test.sqlite", echo=True)
