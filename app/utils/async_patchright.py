import shutil
from pathlib import Path

from patchright.async_api import (
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)


async def wrapper(spider, func, *args, **kwargs):
    await spider.start()
    try:
        return await func(*args, **kwargs)
    finally:
        await spider.finish()


class Patchright:
    page: Page
    context: BrowserContext
    playwright: Playwright

    def __init__(
            self,
            name: str,
            headless: bool,
    ):
        self.headless = headless
        self._name = name
        self.user_data_dir = Path(f"/tmp/playwright/{self._name}").absolute().as_posix()

    async def start(self) -> BrowserContext:
        args = ["--window-size=1920,1080"]
        self.playwright = await async_playwright().start()
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            no_viewport=True,
            channel="chromium",
            args=args,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        )
        return self.context

    async def finish(self) -> None:
        await self.playwright.stop()
        shutil.rmtree(self.user_data_dir)