import logging
from enum import Enum
from typing import Annotated, Optional
from uuid import UUID

from aiogram import Bot
from aiogram.types import BufferedInputFile
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel

from giveaway_bot.application.interactors.giveaway.get_giveaway_steps import GetGiveawayStepsInteractor
from giveaway_bot.application.interactors.postback.change_subscription import EditSubscriptionInteractor
from giveaway_bot.application.interactors.postback.save_postback import SavePostbackInteractor
from giveaway_bot.infrastructure.media_storage import MediaStorage

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
    sub2: str
    status: StatusEnum
    click_id: Optional[str] = None
    payout: Optional[float] = None
    payout_total: Optional[float] = None
    payout_currency: Optional[str] = None
    transaction_id: Optional[str] = None


@router.post("/postback")
async def postback(
        bot: FromDishka[Bot],
        interactor: FromDishka[SavePostbackInteractor],
        edit_subscription_interactor: FromDishka[EditSubscriptionInteractor],
        get_giveaway_interactor: FromDishka[GetGiveawayStepsInteractor],
        storage: FromDishka[MediaStorage],
        data: PostbackModel = Query()
):
    if not data.sub1:
        raise HTTPException(status_code=400, detail="sub1 is required")
    await interactor.execute(tg_id=data.sub1, postback_data=data.model_dump())
    giveawya_id = UUID(data.sub2)
    giveawya = await get_giveaway_interactor.execute(giveaway_id=giveawya_id, user_id=data.sub1)
    logger.info("Received postback data: %s", data)
    if data.status == StatusEnum.subscribe:
        await edit_subscription_interactor.execute(tg_id=data.sub1, is_subscribed=True)
        if giveawya.success_step.media:
            file = giveawya.success_step.media[0]
            media = await storage.get_media(file.filename)
            media.seek(0)
            await bot.send_photo(chat_id=data.sub1, photo=BufferedInputFile(file=media.read(), filename=file.filename),
                                 caption=giveawya.success_step.text),
        else:
            await bot.send_message(chat_id=data.sub1, text=giveawya.success_step.text)
    elif data.status == StatusEnum.unsubscribe:
        await edit_subscription_interactor.execute(tg_id=data.sub1, is_subscribed=False)

    return {"status": "ok"}


@router.get("/test")
async def test():
    return {"status": "ok"}
