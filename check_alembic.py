import asyncio
import sys
from sqlalchemy import text

from api.core.database import async_session

async def check_alembic_version():
    """Check if the alembic_version table exists and its contents"""
    try:
        print("Checking Alembic version table...")
        
        # Get a database session
        async with async_session() as session:
            # Check if the alembic_version table exists
            try:
                result = await session.execute(text("SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'alembic_version')"))
                exists = result.scalar()
                
                if exists:
                    print("alembic_version table exists!")
                    # Check the version
                    result = await session.execute(text("SELECT version_num FROM alembic_version"))
                    versions = result.scalars().all()
                    print(f"Current versions in alembic_version table: {versions}")
                else:
                    print("alembic_version table does not exist.")
                    
            except Exception as e:
                print(f"Error checking alembic version: {e}")
                return
        
    except Exception as e:
        print(f"Error during check: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(check_alembic_version())