import secrets
from typing import List, Optional, Union

from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import Card, CreateCardData, Hit


async def create_card(data: CreateCardData, wallet_id: str) -> Card:
    card_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO boltcards.cards (
            id,
            wallet,
            card_name,
            uid,
            counter,
            withdraw,
            k0,
            k1,
            k2,
            otp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            card_id,
            wallet_id,
            data.card_name,
            data.uid.upper(),
            data.counter,
            data.withdraw,
            data.k0,
            data.k1,
            data.k2,
            secrets.token_hex(16),
        ),
    )
    card = await get_card(card_id)
    assert card, "Newly created card couldn't be retrieved"
    return card


async def update_card(card_id: str, **kwargs) -> Optional[Card]:
    if "is_unique" in kwargs:
        kwargs["is_unique"] = int(kwargs["is_unique"])
    if "uid" in kwargs:
        kwargs["uid"] = kwargs["uid"].upper()
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE boltcards.cards SET {q} WHERE id = ?",
        (*kwargs.values(), card_id),
    )
    row = await db.fetchone("SELECT * FROM boltcards.cards WHERE id = ?", (card_id,))
    return Card(**row) if row else None


async def get_cards(wallet_ids: Union[str, List[str]]) -> List[Card]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM boltcards.cards WHERE wallet IN ({q})", (*wallet_ids,)
    )

    return [Card(**row) for row in rows]


async def get_all_cards() -> List[Card]:
    rows = await db.fetchall(f"SELECT * FROM boltcards.cards")

    return [Card(**row) for row in rows]


async def get_card(card_id: str) -> Optional[Card]:
    row = await db.fetchone("SELECT * FROM boltcards.cards WHERE id = ?", (card_id,))
    if not row:
        return None

    card = dict(**row)

    return Card.parse_obj(card)


async def get_card_by_uid(card_uid: str) -> Optional[Card]:
    row = await db.fetchone(
        "SELECT * FROM boltcards.cards WHERE uid = ?", (card_uid.upper(),)
    )
    if not row:
        return None

    card = dict(**row)

    return Card.parse_obj(card)


async def get_card_by_otp(otp: str) -> Optional[Card]:
    row = await db.fetchone("SELECT * FROM boltcards.cards WHERE otp = ?", (otp,))
    if not row:
        return None

    card = dict(**row)

    return Card.parse_obj(card)


async def delete_card(card_id: str) -> None:
    await db.execute("DELETE FROM boltcards.cards WHERE id = ?", (card_id,))


async def update_card_counter(counter: int, id: str):
    await db.execute(
        "UPDATE boltcards.cards SET counter = ? WHERE id = ?",
        (counter, id),
    )


async def update_card_otp(otp: str, id: str):
    await db.execute(
        "UPDATE boltcards.cards SET otp = ? WHERE id = ?",
        (otp, id),
    )


async def get_hit(hit_id: str) -> Optional[Hit]:
    row = await db.fetchone(f"SELECT * FROM boltcards.hits WHERE id = ?", (hit_id))
    if not row:
        return None

    hit = dict(**row)

    return Hit.parse_obj(hit)


async def get_hits(cards_ids: Union[str, List[str]]) -> List[Hit]:
    q = ",".join(["?"] * len(cards_ids))
    rows = await db.fetchall(
        f"SELECT * FROM boltcards.hits WHERE card_id IN ({q})", (*cards_ids,)
    )

    return [Hit(**row) for row in rows]


async def create_hit(card_id, ip, useragent, old_ctr, new_ctr) -> Hit:
    hit_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO boltcards.hits (
            id,
            card_id,
            ip,
            useragent,
            old_ctr,
            new_ctr
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            hit_id,
            card_id,
            ip,
            useragent,
            old_ctr,
            new_ctr,
        ),
    )
    hit = await get_hit(hit_id)
    assert hit, "Newly recorded hit couldn't be retrieved"
    return hit