import asyncio
import os

from app.scraping import Querencia
from app.utils.async_patchright import wrapper
from dotenv import load_dotenv

load_dotenv()


async def main():
    querencia = Querencia(os.getenv("PARAMETRO_PESQUISA"))
    await wrapper(querencia, querencia.scraping)


if __name__ == "__main__":
    asyncio.run(main())
