"""
 消息类型
    UserMessage （用户）
    BotMessage （机器人）

to_dict： 将实例对象转成字典对象
from_dict： 将字典对象转成实例对象

"""
from typing import  Dict, Any
from enum import Enum
from dataclasses import field, dataclass


class MessageType(Enum):
    TEXT = "text"           # 文本类型
    OBJECT = "object"       # 对象类型

@dataclass(slots=True)  # 访问速度比较快/内存占用空间少 __dict__
class FocusedObject:
    """
        聚焦对象
    """
    id: str
    type: str
    title: str=""
    attributes: Dict[str, Any]=field(default_factory=dict)


    def to_dict(self) -> Dict[str, Any]:
         """
            **序列化（Serialization）**：将程序内存中「结构化的数据对象」（比如 Python 的类实例、字典、列表）转换为一种**可存储、可传输**的格式（比如 JSON 字符串、二进制字节流）的过程。
            **反序列化（Deserialization）**：序列化的逆过程，将存储 / 传输得到的格式数据，重新还原为程序内存中可以直接操作的数据对象。
         """
         return {
             "id": self.id,
             "type": self.type,
             "title": self.title,
             "attributes": dict(self.attributes) # 浅拷贝
         }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FocusedObject": # 前向引用 添加一个字符串 作为一个字面量

        return cls(
            id=data["id"],
            type=data["type"],
            title=data.get("title", ""),
            attributes=data.get("attributes", {})
        )


@dataclass(slots=True)
class UserMessage:
    sender_id: str      #用户ID（必填）
    message_id: str     #消息ID（必填）
    type: MessageType   #消息类型（text or object） 必填字段
    text: str | None = None  # 文本消息
    object: FocusedObject | None = None  # 对象类型的消息

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "message_id": self.message_id,
            "type": self.type,
            "text": self.text,
            "object": self.object.to_dict() if self.object else None

        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserMessage":

        return cls(
            sender_id = data["sender_id"],
            message_id = data["message_id"],
            type = MessageType(data["type"]),
            text = data.get("text"),
            object = FocusedObject.from_dict(data['object']) if data.get("object") else None
        )

@dataclass(slots=True)
class BotMessage:
    text: str | None = None
    object: FocusedObject | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "object": self.object.to_dict() if self.object else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BotMessage":

        return cls(
            text = data.get("text"),
            object = FocusedObject.from_dict(data['object']) if data.get("object") else None
        )