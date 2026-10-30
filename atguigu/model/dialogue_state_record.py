from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped, mapped_column

from atguigu.model.base import Base


class DialogueStateRecord(Base):
    __tablename__ = 'dialogue_states'
    sender_id: Mapped[str] = mapped_column(primary_key=True)
    state_json: Mapped[str] = mapped_column(TEXT, nullable=False, default={}) # 数据库长文本类型