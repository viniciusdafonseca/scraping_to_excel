import asyncio
from app.scraping import Querencia
from app.utils.async_patchright import wrapper
from dotenv import load_dotenv

load_dotenv()


async def main():
    querencia = Querencia("43.383.928/0001-05")
    await wrapper(querencia, querencia.scraping)


if __name__ == "__main__":
    asyncio.run(main())
