import re

from bs4 import BeautifulSoup

from app.utils.async_patchright import Patchright
from app.utils.captcha import AntiCaptcha


class Querencia:

    _url_base = "https://www.gp.srv.br/tributario/querencia/"

    def __init__(self, cpf_cnpj: str) -> None:
        self._cpf_cnpj = re.sub(r"\D", "", cpf_cnpj)
        self.playwright = Patchright(self._cpf_cnpj, headless=False)
        self._url = (
            "https://www.gp.srv.br/tributario/querencia/portal_serv_servico?7,61"
        )
        self._captcha = AntiCaptcha()

    async def start(self):
        self.context = await self.playwright.start()
        self.page = await self.context.new_page()

    async def finish(self):
        await self.playwright.finish()

    async def _solve_captcha(self) -> None:
        """
        Resolve um CAPTCHA capturando sua imagem, processa via serviço externo
        e preenche o resultado no campo adequado da página web.

        :return: None
        :rtype: NoneType
        """
        img = await self.page.locator(
            'xpath=//*[@id="W0005W0006TXTKAPTCHA"]/img'
        ).screenshot()
        resolved_captcha = await self._captcha.image_captcha(img)
        await self.page.fill("#W0005W0006vVALOR_IMAGEM", resolved_captcha)

    async def _login_sistema(self) -> BeautifulSoup:
        """
        Faz login no sistema e retorna o conteúdo da página no formato do BeautifulSoup.
        :return: Conteúdo HTML parseado.
        :rtype: BeautifulSoup
        """
        await self.page.goto(self._url)

        await self.page.fill("#W0005W0006vCAMPO_00010001", self._cpf_cnpj)
        await self._solve_captcha()

        await self.page.click("#W0005W0006BTN_CONSULTAR2")
        await self.page.wait_for_load_state("domcontentloaded", timeout=120000)
        return BeautifulSoup(await self.page.content(), "html.parser")

    async def scraping(self):
        soup = await self._login_sistema()
        print(soup)
