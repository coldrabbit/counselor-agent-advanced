from sqlalchemy.orm import Session
from app.models.talk_record import TalkRecord
from app.repositories.base import BaseRepository


class TalkRecordRepository(BaseRepository[TalkRecord]):
    def __init__(self, db: Session):
        super().__init__(TalkRecord, db)

    def list_all(self):
        return super().list_all(order_by=TalkRecord.created_at.desc())

    def update_status(self, record: TalkRecord, status: str) -> TalkRecord:
        return self.update(record, status=status)
