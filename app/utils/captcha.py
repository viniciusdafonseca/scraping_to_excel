import os
from asyncio import sleep
from base64 import b64encode

import httpx
from httpx import AsyncClient
from loguru import logger


class AntiCaptcha:
    def __init__(self):
        self.solver_key = os.getenv("ANTICAPTCHA_KEY")
        self.session = AsyncClient(
            follow_redirects=True,
            timeout=200,
            verify=False,
            http2=True,
        )
        self.session.base_url = "https://api.anti-captcha.com/"
        self.task_id = None

    async def _make_request(self, task_data: dict[str, str]) -> str:
        payload = {"clientKey": self.solver_key, "task": task_data}
        try:
            response = await self.session.post("/createTask", json=payload)
        except (httpx.ReadError, httpx.WriteError, httpx.ConnectError):
            await sleep(0.5)
            response = await self.session.post("/createTask", json=payload)

        # Adquire as informações da requisição
        res: dict[str, str] = response.json()

        # Verifica se a requisição foi bem sucedida
        if res["errorId"] != 0:
            detail = res["errorDescription"]
            raise Exception("AntiCaptcha", res.get("taskId", 0), detail)

        logger.debug(f"Task {res['taskId']!r} criada com sucesso!")

        return res["taskId"]

    async def _create_tasks_imagecaptcha(self, content: bytes) -> str:
        task_data = {
            "type": "ImageToTextTask",
            "body": b64encode(content).decode("ascii"),
            "phrase": False,
            "case": False,
            "numeric": 0,
            "math": False,
            "minLength": 0,
            "maxLength": 0,
            "comment": False,
        }
        return await self._make_request(task_data)

    async def _get_task_result(self, task_id: str) -> dict[str, str] | None:
        await sleep(0.5)
        payload = {"clientKey": self.solver_key, "taskId": task_id}
        try:
            task_check = await self.session.post("/getTaskResult", json=payload)
        except (httpx.ReadError, httpx.WriteError, httpx.ConnectError):
            await sleep(0.5)
            task_check = await self.session.post("/getTaskResult", json=payload)

        task_check = task_check.json()

        if task_check["errorId"] != 0:
            detail = task_check["errorDescription"]
            raise Exception("AntiCaptcha", task_id, detail)

        if task_check["status"] == "processing":
            return await self._get_task_result(task_id)

        if task_check["status"] == "ready":
            logger.info(f"Task {task_id!r} resolvida com sucesso!")
            return task_check["solution"]

    async def image_captcha(self, content: bytes):
        self.task_id = await self._create_tasks_imagecaptcha(content)
        solved = await self._get_task_result(self.task_id)
        return solved["text"]
