import asyncio
import os

from app.scraping import Scraping
from app.utils.async_patchright import wrapper
from dotenv import load_dotenv

load_dotenv()


async def main():
    scraping = Scraping(os.getenv("PARAMETRO_PESQUISA"))
    await wrapper(scraping, scraping.run)


if __name__ == "__main__":
    asyncio.run(main())
