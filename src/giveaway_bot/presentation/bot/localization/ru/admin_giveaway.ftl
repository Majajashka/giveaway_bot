input-giveaway-duration =
    ❌ Неверный формат.

    Введите дату окончания в формате <b>ДД-ММ-ГГГГ ЧЧ:ММ</b> (например: <code>20-08-2025 18:30</code>)

giveaway-list =
    Список розыгрышей:

giveaway-admin-info =
    🎁 <b>{ $title }</b>
    🆔 ID: <code>{ $id }</code>
    🗓 Создано: <b>{ DATETIME($created_at, dateStyle: "short", timeStyle: "short") }</b>
    📅 Дата окончания: <b>{ DATETIME($ends_at, dateStyle: "short", timeStyle: "short") }</b>
    ⌛ Осталось: <b>{ $time_left }</b>

    📝 <b>Описание:</b>
    <pre>{ $description }</pre>

