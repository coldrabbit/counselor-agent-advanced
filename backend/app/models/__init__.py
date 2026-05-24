from app.db.database import Base
from app.models.notice import Notice
from app.models.task import Task
from app.models.counselor import CounselorProfile
from app.models.talk_record import TalkRecord
from app.models.class_model import Class
from app.models.student import Student
from app.models.template import NoticeTemplate
from app.models.risk_record import RiskRecord


def init_db():
    Base.metadata.create_all(bind=Base.metadata.bind)
