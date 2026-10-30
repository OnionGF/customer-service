from atguigu.domain.messages import UserMessage, ProcessResult, BotMessage
from atguigu.domain.state import DialogueState


class DialogueEngine:

    async def hand_dialogue(self, dialogue_state: DialogueState,
                                  user_message: UserMessage) -> ProcessResult:
        return ProcessResult(
            sender_id=user_message.sender_id,
            message_id=user_message.message_id,
            messages=[
                BotMessage(text="我是智能小客服"),
                BotMessage(text="欢迎你来到这里")
            ]
        )
