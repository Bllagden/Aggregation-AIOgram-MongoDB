import asyncio

import dotenv

from aggregation import aggregate_salaries
from data.input_json import json_to_dict
from db import collection


async def main():
    _json = await json_to_dict("input_3.json")
    print(_json, "\n")

    results = await aggregate_salaries(
        collection,
        _json["dt_from"],
        _json["dt_upto"],
        _json["group_type"],
    )
    print(results)


if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    asyncio.run(main())
