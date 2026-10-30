from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.infrastructure import database
from atguigu.repository.dialogue_state_repository import DialogueStateRepository
from atguigu.service.dialogue_service import DialogueService

async def get_engine():
    return DialogueEngine()

async def get_session():
    async with database.async_session() as session:
        yield session

async def get_dialogue_state_repository(session: AsyncSession = Depends(get_session)):
    return DialogueStateRepository(session=session)

async def get_dialogue_service(dialogue_state_repository: DialogueStateRepository = Depends(get_dialogue_state_repository),
                        dialogue_engine: DialogueEngine = Depends(get_engine)
                         ) -> DialogueService:
    return DialogueService(dialogue_state_repository=dialogue_state_repository, dialogue_engine=dialogue_engine)