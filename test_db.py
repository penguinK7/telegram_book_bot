from db_handler.db_class import objects, User, create_tables
import asyncio

async def test():
    await create_tables()
    user, created = await objects.get_or_create(User, user_id=123, defaults={'is_admin': False})
    print(f"User created: {created}")

asyncio.run(test())