"""Generate realistic data and populate MongoDB collections."""

import random
from datetime import datetime, timedelta

from pymongo.database import Database as MongoDatabase

from utils.logger import get_logger
from config.settings import (
    MONGO_SEED, MONGO_NUM_USERS, MONGO_NUM_SESSIONS,
    MONGO_NUM_EVENTS, MONGO_NUM_TICKETS, MONGO_NUM_REVIEWS,
)

log = get_logger(__name__)

PAGES = [
    "/home", "/products", "/products/42", "/products/101", "/products/205",
    "/cart", "/checkout", "/account", "/orders", "/support",
    "/about", "/blog", "/blog/post-1", "/blog/post-2", "/faq",
    "/search", "/categories", "/deals", "/wishlist", "/settings",
]

ACTIONS = [
    "login", "logout", "view_product", "add_to_cart", "remove_from_cart",
    "purchase", "search", "filter", "sort", "write_review",
    "scroll", "click_banner", "share", "bookmark", "compare",
]

DEVICES = ["mobile", "desktop", "tablet"]

EVENT_TYPES = [
    "click", "page_view", "scroll", "form_submit", "error",
    "api_call", "notification", "session_start", "session_end", "purchase",
]

ISSUE_TYPES = ["payment", "delivery", "refund", "account", "technical", "other"]
TICKET_STATUSES = ["open", "in_progress", "resolved", "closed"]

PRODUCT_IDS = [f"prod_{i:03d}" for i in range(1, 51)]

REVIEW_TEXTS = [
    "Отличный товар, работает как нужно!",
    "Качество среднее, но за свою цену нормально.",
    "Не рекомендую, сломался через неделю.",
    "Доставка быстрая, товар соответствует описанию.",
    "Хороший продукт, буду заказывать ещё.",
    "Упаковка была повреждена, но товар целый.",
    "Превзошёл ожидания, очень доволен!",
    "Нормальный товар, ничего особенного.",
    "Плохое качество материалов.",
    "Идеальное соотношение цена-качество.",
    "Great product, works perfectly!",
    "Average quality but acceptable for the price.",
    "Not recommended, broke after a week.",
    "Fast delivery, product matches description.",
    "Good product, will order again.",
]

MODERATION_STATUSES = ["pending", "approved", "rejected"]
FLAGS = ["spam", "offensive", "contains_images", "suspicious", "duplicate", "low_quality"]

SUPPORT_MESSAGES_USER = [
    "Не могу оплатить заказ.",
    "Когда будет доставка?",
    "Хочу вернуть товар.",
    "Не приходит код подтверждения.",
    "Проблема с авторизацией.",
    "Товар не соответствует описанию.",
    "Как изменить адрес доставки?",
    "Заказ пришёл повреждённым.",
]

SUPPORT_MESSAGES_AGENT = [
    "Пожалуйста, уточните способ оплаты.",
    "Ваш заказ будет доставлен в течение 3 рабочих дней.",
    "Оформите возврат через личный кабинет.",
    "Проверьте папку «Спам» в вашей почте.",
    "Попробуйте сбросить пароль.",
    "Мы отправим замену в ближайшее время.",
    "Адрес можно изменить до момента отправки.",
    "Приносим извинения за неудобства, оформим компенсацию.",
]


def _random_datetime(start: datetime, end: datetime, rng: random.Random) -> datetime:
    delta = end - start
    seconds = int(delta.total_seconds())
    return start + timedelta(seconds=rng.randint(0, max(seconds, 1)))


def generate_all(db: MongoDatabase) -> dict:
    """Generate and insert all collections. Returns insertion counts."""
    rng = random.Random(MONGO_SEED)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31, 23, 59, 59)

    user_ids = [f"user_{i:04d}" for i in range(1, MONGO_NUM_USERS + 1)]
    counts = {}

    # ── user_sessions ──
    sessions = []
    for i in range(1, MONGO_NUM_SESSIONS + 1):
        st = _random_datetime(start_date, end_date, rng)
        et = st + timedelta(minutes=rng.randint(1, 120))
        n_pages = rng.randint(1, 8)
        n_actions = rng.randint(1, 6)
        sessions.append({
            "session_id": f"sess_{i:05d}",
            "user_id": rng.choice(user_ids),
            "start_time": st,
            "end_time": et,
            "pages_visited": [rng.choice(PAGES) for _ in range(n_pages)],
            "device": rng.choice(DEVICES),
            "actions": [rng.choice(ACTIONS) for _ in range(n_actions)],
        })
    db.drop_collection("user_sessions")
    db.user_sessions.insert_many(sessions)
    counts["user_sessions"] = len(sessions)
    log.info("Inserted %d user_sessions", len(sessions))

    # ── event_logs ──
    events = []
    for i in range(1, MONGO_NUM_EVENTS + 1):
        ts = _random_datetime(start_date, end_date, rng)
        etype = rng.choice(EVENT_TYPES)
        detail_page = rng.choice(PAGES)
        events.append({
            "event_id": f"evt_{i:05d}",
            "timestamp": ts,
            "event_type": etype,
            "details": {"page": detail_page, "duration_ms": rng.randint(50, 5000)},
        })
    db.drop_collection("event_logs")
    db.event_logs.insert_many(events)
    counts["event_logs"] = len(events)
    log.info("Inserted %d event_logs", len(events))

    # ── support_tickets ──
    tickets = []
    for i in range(1, MONGO_NUM_TICKETS + 1):
        created = _random_datetime(start_date, end_date, rng)
        status = rng.choice(TICKET_STATUSES)
        n_msgs = rng.randint(1, 5)
        messages = []
        msg_time = created
        for m_idx in range(n_msgs):
            sender = "user" if m_idx % 2 == 0 else "support"
            msg_text = rng.choice(SUPPORT_MESSAGES_USER if sender == "user" else SUPPORT_MESSAGES_AGENT)
            messages.append({
                "sender": sender,
                "message": msg_text,
                "timestamp": msg_time,
            })
            msg_time = msg_time + timedelta(minutes=rng.randint(10, 480))
        updated = msg_time
        tickets.append({
            "ticket_id": f"ticket_{i:05d}",
            "user_id": rng.choice(user_ids),
            "status": status,
            "issue_type": rng.choice(ISSUE_TYPES),
            "messages": messages,
            "created_at": created,
            "updated_at": updated,
        })
    db.drop_collection("support_tickets")
    db.support_tickets.insert_many(tickets)
    counts["support_tickets"] = len(tickets)
    log.info("Inserted %d support_tickets", len(tickets))

    # ── user_recommendations ──
    recommendations = []
    for uid in user_ids:
        n_products = rng.randint(2, 8)
        recommendations.append({
            "user_id": uid,
            "recommended_products": rng.sample(PRODUCT_IDS, min(n_products, len(PRODUCT_IDS))),
            "last_updated": _random_datetime(start_date, end_date, rng),
        })
    db.drop_collection("user_recommendations")
    db.user_recommendations.insert_many(recommendations)
    counts["user_recommendations"] = len(recommendations)
    log.info("Inserted %d user_recommendations", len(recommendations))

    # ── moderation_queue ──
    reviews = []
    for i in range(1, MONGO_NUM_REVIEWS + 1):
        n_flags = rng.randint(0, 3)
        reviews.append({
            "review_id": f"rev_{i:05d}",
            "user_id": rng.choice(user_ids),
            "product_id": rng.choice(PRODUCT_IDS),
            "review_text": rng.choice(REVIEW_TEXTS),
            "rating": rng.randint(1, 5),
            "moderation_status": rng.choice(MODERATION_STATUSES),
            "flags": rng.sample(FLAGS, n_flags) if n_flags > 0 else [],
            "submitted_at": _random_datetime(start_date, end_date, rng),
        })
    db.drop_collection("moderation_queue")
    db.moderation_queue.insert_many(reviews)
    counts["moderation_queue"] = len(reviews)
    log.info("Inserted %d moderation_queue entries", len(reviews))

    log.info("Data generation complete: %s", counts)
    return counts
