import logging
from typing import Annotated

from aiogram import Bot
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from giveaway_bot.application.interactors.postback.save_postback import SavePostbackInteractor

router = APIRouter(
    tags=["postback"],
    route_class=DishkaRoute
)

logger = logging.getLogger(__name__)


class PostbackModel(BaseModel):
    user_id: int
    sub1: int  # tg_id
    event: str


@router.post("/postback", )
async def postback(data: PostbackModel, bot: FromDishka[Bot], interactor: FromDishka[SavePostbackInteractor]) -> None:
    if not data.sub1:
        raise HTTPException(status_code=400, detail="sub1 is required")

    logger.info("Received postback data: %s", data)
    await interactor.execute(tg_id=data.sub1, postback_data=data.model_dump())
    await bot.send_message(chat_id=data.sub1, text=f"Вы успешно прошли регистрацию!")
