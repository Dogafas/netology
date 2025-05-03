import asyncio
import datetime
from typing import Sequence

import aiohttp
from more_itertools import chunked

from models import Session, SwapiPeople, close_orm, init_orm

MAX_REQUESTS = 5


async def get_people(person_id, session):

    response = await session.get(f"https://swapi.py4e.com/api/people/{person_id}/")
    json_data = await response.json()

    return json_data


async def insert_people(people: Sequence[dict]):
    async with Session() as session:
        swapi_people_list = [SwapiPeople(json=json_item) for json_item in people]
        session.add_all(swapi_people_list)
        await session.commit()


async def main():
    await init_orm()
    ids_chunks = chunked(range(1, 101), MAX_REQUESTS)

    async with aiohttp.ClientSession() as session:
        for id_chunk in ids_chunks:
            coros = [get_people(people_id, session) for people_id in id_chunk]
            people_json_list = await asyncio.gather(*coros)
            insert_people_coro = insert_people(people_json_list)
            insert_people_task = asyncio.create_task(insert_people_coro)
        all_tasks = asyncio.all_tasks()
        current_task = asyncio.current_task()
        all_tasks.remove(current_task)
        await asyncio.gather(*all_tasks)

    await close_orm()


start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)
