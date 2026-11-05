import json

from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.domain.state import DialogueState
from atguigu.models.dialogue_state import DialogueStateRecord


class DialogueStateRepository:
    """
    DialogueStateRepository 操作数据库层
    # 操作数据库和会话AsyncSession注入进来

    # orm ：如果简单curd操作不需要写sql语句，调用sqlalchemy方法实现
    #       如果有复杂需求，编写sql语句，比如多表查询，分组等
    # load_state 方法： 根据sender_id查询数据
    # save_state 保存数据（如果sender_id不存在添加，如果存在更新）
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    # 根据sender_id 去查数据
    async def load(self, sender_id: str) -> DialogueState:
        """
        读操作
        :return:
        """
        # 1、定义 sql
        # SELECT * FROM dialogue_states WHERE sender_id=?
        # sql1 = "SELECT * FROM dialogue_states WHERE sender_id=:sid"
        # result1 = await self.session.execute(sql1,{'sid':sender_id})

        # sqlalchemy方法构建sql语句
        sql = select(DialogueStateRecord).where(DialogueStateRecord.sender_id == sender_id)

        # 2、调用session方法 执行sql
        result = await self.session.execute(sql)

        # 3、获取结果
        sate = result.scalar_one_or_none()

        if sate:
            state_dict = json.loads(sate.state_json)
            return DialogueState.from_dict(state_dict)

        return DialogueState(sender_id=sender_id)

    # 保存数据
    async def save(self, dialogue_state: DialogueState):
        """
        写操作(插入、修改
        传统： 插入之前先查询该条件（sender_id）对应的记录是否存在，如果不存在 则插入，反正修改
        进阶：负责将插入sql直接升级为修改sql（主键重复机制判断）
        :return:
        """

        # 1、定义插入的sql语句
        state_json_str = json.dumps(dialogue_state.to_dict())
        insert_stmt = insert(DialogueStateRecord).values(
            sender_id=dialogue_state.sender_id,
            state_json=state_json_str
        )
        # 2、升级update语句的sql
        # 需求：如果sender_id不存在添加，如果存在更新
        # 实现方式一：
        # 1 根据sender_id查询数据库，得到结果
        # 2 对查询结果判断，如果不存在结果，添加
        # 3              如果结果存在，更新 （构建更新sql语句）

        # 实现方式二：
        # 使用sqlalchemy封装方式实现
        updated_stmt = insert_stmt.on_duplicate_key_update(
            state_json=insert_stmt.inserted.state_json
        )
        # 3、执行sql
        await self.session.execute(updated_stmt)

        # 4、提交
        await self.session.commit()