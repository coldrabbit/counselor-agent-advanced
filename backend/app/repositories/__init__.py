from app.repositories.base import BaseRepository
from app.repositories.notice import NoticeRepository
from app.repositories.talk_record import TalkRecordRepository
from app.repositories.counselor import CounselorRepository
from app.repositories.task import TaskRepository
from app.repositories.classes import ClassRepository
from app.repositories.students import StudentRepository
from app.repositories.templates import TemplateRepository
from app.repositories.risk import RiskRepository
from app.repositories.document import DocumentRepository
from app.repositories.user import UserRepository

__all__ = [
    "BaseRepository",
    "NoticeRepository",
    "TalkRecordRepository",
    "CounselorRepository",
    "TaskRepository",
    "ClassRepository",
    "StudentRepository",
    "TemplateRepository",
    "RiskRepository",
    "DocumentRepository",
    "UserRepository",
]
