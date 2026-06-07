from app.db.models import LogHistoryDB
from app.models import LogActivityCardOut, LogActivityOut, LogHistoryOut, LogHistoryUserOut


def history_to_dto(log: LogHistoryDB) -> LogHistoryOut:
    return LogHistoryOut(
            user=LogHistoryUserOut(
                id=log.user.id,
                username=log.user.username,
                is_admin=log.user.is_admin
            ),
            user_interacted=LogHistoryUserOut(
                id=log.user_interacted.id,
                username=log.user_interacted.username,
                is_admin=log.user_interacted.is_admin
            ) if log.user_interacted else None,
            description=log.description,
            type=log.type,
            money_exchange=log.money_exchange,
            date=log.date,
            activities=[
                LogActivityOut(
                    id_user=activity.user.id,
                    card=LogActivityCardOut(
                        id=activity.user_card.card.id,
                        name=activity.user_card.card.name,
                        price=activity.user_card.card.price/100,
                        frontcard=activity.user_card.card.frontcard
                    ) if activity.user_card else None,
                    id_log_history=activity.log_history.id,
                    action=activity.action,
                    price=activity.price/100,
                    psa=activity.psa
                ) for activity in log.log_activity
            ]
        )