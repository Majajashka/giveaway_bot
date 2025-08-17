import logging
from enum import Enum
from typing import Annotated, Optional

from aiogram import Bot
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from giveaway_bot.application.interactors.postback.change_subscription import EditSubscriptionInteractor
from giveaway_bot.application.interactors.postback.save_postback import SavePostbackInteractor

router = APIRouter(
    tags=["postback"],
    route_class=DishkaRoute
)

logger = logging.getLogger(__name__)


class StatusEnum(str, Enum):
    registration = "registration"
    first_buy = "first_buy"
    subscribe = "subscribe"
    unsubscribe = "unsubscribe"
    rebill = "rebill"
    chargeback = "chargeback"
    refund = "refund"


class PostbackModel(BaseModel):
    sub1: int
    status: StatusEnum
    click_id: Optional[str] = None
    payout: Optional[float] = None
    payout_total: Optional[float] = None
    payout_currency: Optional[str] = None
    transaction_id: Optional[str] = None




@router.post("/postback", )
async def postback(data: PostbackModel, bot: FromDishka[Bot], interactor: FromDishka[SavePostbackInteractor], edit_subscription_interactor: FromDishka[EditSubscriptionInteractor]) -> None:
    if not data.sub1:
        raise HTTPException(status_code=400, detail="sub1 is required")

    logger.info("Received postback data: %s", data)
    if data.status == StatusEnum.subscribe:
        await edit_subscription_interactor.execute(tg_id=data.sub1, is_subscribed=True)
    elif data.status == StatusEnum.unsubscribe:
        await edit_subscription_interactor.execute(tg_id=data.sub1, is_subscribed=False)
    await interactor.execute(tg_id=data.sub1, postback_data=data.model_dump())
    await bot.send_message(chat_id=data.sub1, text=f"Вы успешно прошли регистрацию!")
