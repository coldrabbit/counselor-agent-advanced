from app.repositories.base import BaseRepository
from app.repositories.notice import NoticeRepository
from app.repositories.talk_record import TalkRecordRepository
from app.repositories.counselor import CounselorRepository
from app.repositories.task import TaskRepository

__all__ = [
    "BaseRepository",
    "NoticeRepository",
    "TalkRecordRepository",
    "CounselorRepository",
    "TaskRepository",
]
