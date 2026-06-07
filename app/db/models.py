from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class UserDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    username: str = Field(index=True, unique=True)
    password: str = Field(index=True)  
    email: str = Field(index=True, unique=True)
    money: int = Field(default=0, index=True)
    opened_boosters: int = Field(default=0, index=True)
    exchanges: int | None = Field(default=0, index=True)
    is_admin: bool = Field(default=False, index=True)

    card_market: list["CardMarketDB"] = Relationship(back_populates="user", cascade_delete=True)
    user_cards: list["UserCardDB"] = Relationship(back_populates="user", cascade_delete=True)
    log_activity: list["LogActivityDB"] = Relationship(back_populates="user")
    log_history: list["LogHistoryDB"] = Relationship(back_populates="user", sa_relationship_kwargs={"foreign_keys": "LogHistoryDB.id_user"})
    log_history_interacted: list["LogHistoryDB"] = Relationship(back_populates="user_interacted", sa_relationship_kwargs={"foreign_keys": "LogHistoryDB.id_user_interacted"})


class CardDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_expansion: int = Field(index=True, foreign_key="expansiondb.id", ondelete="CASCADE")
    name: str = Field(index=True)
    rarity: str = Field(index=True)
    price: int = Field(index=True)
    card_number: int = Field(index=True)
    frontcard: str = Field(index=True)
    backcard: str = Field(index=True)

    user_cards: list["UserCardDB"] = Relationship(back_populates="card")
    card_market: list["CardMarketDB"] = Relationship(back_populates="card")
    expansion: "ExpansionDB" = Relationship(back_populates="cards")
    log_activity: list["LogActivityDB"] = Relationship(back_populates="card")


class ExpansionDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_generation: int = Field(index=True, foreign_key="generationdb.id", ondelete="CASCADE")
    name: str = Field(index=True)
    price: int = Field(index=True)
    year: int = Field(index=True)

    generation: "GenerationDB" = Relationship(back_populates="expansions")
    cards: list["CardDB"] = Relationship(back_populates="expansion", cascade_delete=True)


class GenerationDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    year: int = Field(index=True)

    expansions: list["ExpansionDB"] = Relationship(back_populates="generation", cascade_delete=True)


class UserCardDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_user: int = Field(index=True, foreign_key="userdb.id", ondelete="CASCADE")
    price: int = Field(index=True)
    psa: int | None = Field(index=True)
    sold: bool = Field(index=True, default=False)

    id_card: int = Field(default=None, foreign_key="carddb.id")
    card: Optional["CardDB"] = Relationship(back_populates="user_cards")
    user: Optional["UserDB"] = Relationship(back_populates="user_cards")
    card_market: list["CardMarketDB"] = Relationship(back_populates="user_card", cascade_delete=True)


class CardMarketDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_user: int = Field(index=True, foreign_key="userdb.id", ondelete="CASCADE") # User that offers the card
    id_user_card: int = Field(index=True, foreign_key="usercarddb.id", ondelete="CASCADE") # Offer card
    id_card: int | None = Field(index=True, foreign_key="carddb.id") # Demanded card
    psa: int | None = Field(default=None, index=True) # Demanded card psa

    exchange_type: str = Field(index=True) # For sale or exchange
    price: int | None = Field(default=None, index=True) # For sale price

    user: "UserDB" = Relationship(back_populates="card_market")
    user_card: "UserCardDB" = Relationship(back_populates="card_market")
    card: "CardDB" = Relationship(back_populates="card_market")


class LogActivityDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_user: int = Field(index=True, foreign_key="userdb.id")
    id_card: int = Field(index=True, foreign_key="carddb.id")
    id_log_history: int = Field(index=True, foreign_key="loghistorydb.id")
    action: str = Field(index=True)
    price: int = Field(index=True)
    psa: int | None = Field(index=True)

    user: "UserDB" = Relationship(back_populates="log_activity")
    card: "CardDB" = Relationship(back_populates="log_activity")
    log_history: "LogHistoryDB" = Relationship(back_populates="log_activity")


class LogHistoryDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_user: int = Field(index=True, foreign_key="userdb.id")
    id_user_interacted: int | None = Field(index=True, foreign_key="userdb.id")
    description: str = Field(index=True)
    type: str = Field(index=True)
    money_exchange: int = Field(default=0, index=True)
    date: str = Field(default_factory=datetime.now ,index=True)

    log_activity: list["LogActivityDB"] = Relationship(back_populates="log_history")
    user: "UserDB" = Relationship(back_populates="log_history", sa_relationship_kwargs={"foreign_keys": "LogHistoryDB.id_user"})
    user_interacted: "UserDB" = Relationship(back_populates="log_history_interacted", sa_relationship_kwargs={"foreign_keys": "LogHistoryDB.id_user_interacted"})





