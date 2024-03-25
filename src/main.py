import asyncio

import dotenv

from data.input_json import json_to_dict

if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    print(asyncio.run(json_to_dict("input_1.json")))
