import asyncio
import datetime
from typing import Sequence
import aiohttp
from more_itertools import chunked
from models import Session, SwapiPeople, close_orm, init_orm
from tqdm import tqdm


MAX_REQUESTS = 5


async def get_people(person_id: int, session: aiohttp.ClientSession) -> dict | None:
    try:
        # Используем person_id в URL
        async with session.get(
            f"https://swapi.dev/api/people/{person_id}/"
        ) as response:
            if response.status == 404:
                return None  # Пропускаем отсутствующих персонажей
            if response.status != 200:
                print(f"Ошибка для ID {person_id}: {response.status}")
                return None

            json_data = await response.json()

            return {
                "id": person_id,
                "birth_year": json_data.get("birth_year", ""),
                "eye_color": json_data.get("eye_color", ""),
                "films": ", ".join(json_data.get("films", [])),
                "gender": json_data.get("gender", ""),
                "hair_color": json_data.get("hair_color", ""),
                "height": json_data.get("height", ""),
                "homeworld": json_data.get("homeworld", ""),
                "mass": json_data.get("mass", ""),
                "name": json_data.get("name", ""),
                "skin_color": json_data.get("skin_color", ""),
                "species": ", ".join(json_data.get("species", [])),
                "starships": ", ".join(json_data.get("starships", [])),
                "vehicles": ", ".join(json_data.get("vehicles", [])),
            }
    except aiohttp.ClientError as e:
        print(f"Ошибка при запросе ID {person_id}: {e}")
        return None


async def insert_people(people: Sequence[dict]):
    async with Session() as session:
        swapi_people_list = [
            SwapiPeople(**json_item) for json_item in people if json_item
        ]
        if swapi_people_list:
            session.add_all(swapi_people_list)
            await session.commit()


async def main():
    await init_orm()

    # Определяем количество персонажей (можно узнать из API или задать вручную)
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        # Получаем общее количество персонажей
        async with session.get("https://swapi.dev/api/people/") as response:
            if response.status == 200:
                data = await response.json()
                total_people = data.get("count", 100)  # Получаем общее количество
            else:
                total_people = 100  # Запасное значение

        progress_bar = tqdm(total=total_people, desc="Загрузка персонажей")

        # Разбиваем ID на чанки
        ids_chunks = chunked(range(1, total_people + 1), MAX_REQUESTS)

        for id_chunk in ids_chunks:
            coros = [get_people(people_id, session) for people_id in id_chunk]
            people_json_list = await asyncio.gather(*coros)
            await insert_people(people_json_list)

            progress_bar.update(len(id_chunk))

        progress_bar.close()

    await close_orm()


if __name__ == "__main__":
    start = datetime.datetime.now()
    asyncio.run(main())
    print("Execution time:", datetime.datetime.now() - start)
