from models import Base, User, Address
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


def main():
    # 1. 创建引擎  sqlite:轻量级数据库（数据直接存储到文件中：echo=True:执行的各种DDL...语句都可以在控制台）
    engine = create_engine("sqlite:///mydb", echo=True)

    # 2. 创建表
    Base.metadata.create_all(engine)

    # 3. 使用上下文管理器方式使用session对象
    with Session(engine) as session:
        # 避免重复执行时反复插入同一批数据（否则 name='Mr 张' 会有多条）
        if session.scalar(select(User).limit(1)) is None:
            session.add_all([
                User(name="Mr 张", fullname="张三"),
                User(name="sandy", fullname="Sandy Cheeks"),
                User(name="patrick", fullname="Patrick Star"),
            ])
            session.commit()  # 不会自动提交（需要手动提交）---刷到磁盘

    with Session(engine) as session:
        # 4. 查询（定义查询语句）
        stmt = select(User).where(User.name == "Mr 张")
        # 5. 执行查询语句(查询到多条记录)
        # for user in session.scalars(stmt):
        #     print(user)

        # one()：必须恰好 1 条，多了报 MultipleResultsFound，没有报 NoResultFound
        # first()：取第一条，没有则返回 None
        print(session.scalars(stmt).first())
        # print(type(session.scalars(stmt)))


if __name__ == '__main__':
    main()
