from sqlmodel import select
from .database import get_db

db = get_db()


class CatBlock(db.EasyModel, table=True):
    session_mark: str
    cat_name: str

    @classmethod
    def _get(cls, session_mark: str, cat_name: str):
        session = cls.get_session()
        stmt = select(cls).filter_by(
            session_mark=session_mark,
            cat_name=cat_name
        )
        cursor = session.exec(stmt)
        r = cursor.one_or_none()
        return session, r

    @classmethod
    def check(cls, session_mark: str, cat_name: str):
        session, r = cls._get(session_mark, cat_name)
        session.close()
        return not r

    @classmethod
    def add(cls, session_mark: str, cat_name: str):
        session, r = cls._get(session_mark, cat_name)
        if not r:
            r = cls(session_mark=session_mark, cat_name=cat_name)
            session.add(r)
            session.commit()
        session.close()

    @classmethod
    def remove(cls, session_mark: str, cat_name: str):
        session, r = cls._get(session_mark, cat_name)
        if r:
            session.delete(r)
            session.commit()
        session.close()
