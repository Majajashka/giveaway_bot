from aiogram import Bot

CACHE = {}

async def get_required_channels_urls(
    channels: list[int],
    bot: Bot
) -> list[str]:
    now = time.time()
    urls = []
    for channel_id in channels:
        cached = CACHE.get(channel_id)
        if cached and now - cached[1] < CACHE_TTL:
            username = cached[0]
        else:
            try:
                chat = await bot.get_chat(channel_id)
                username = chat.username
                if username:
                    CACHE[channel_id] = (username, now)
            except (ChatNotFound, Forbidden) as e:
                # Падать, если канал не найден или доступ запрещен
                raise e
            except Exception:
                # Для других ошибок игнорируем (например, сетевые проблемы)
                username = None
        if username:
            urls.append(f"https://t.me/{username}")
    return urls