from database.models.bad_words import BadWord
from database.database import get_session
from sqlalchemy import select


def save_bad_word(group_id: int, word: str) -> bool:
    with get_session() as session:

        exists = session.scalar(
            select(BadWord).where(
                BadWord.group_id == group_id,
                BadWord.word == word
            )
        )

        if exists:
            return False

        bad_word = BadWord(
            group_id=group_id,
            word=word,
        )

        session.add(bad_word)
        return True

def get_bad_words(group_id: int):

    with get_session() as session:
            
        stmt = (select(BadWord).where(BadWord.group_id == group_id).order_by(BadWord.id.asc()))
        bad_words = session.scalars(stmt).all()
        
        return bad_words

def delete_bad_word(group_id: int, word: str) -> bool:
    with get_session() as session:
        stmt = select(BadWord).where(
            BadWord.group_id == group_id,
            BadWord.word == word
        )

        bad_word = session.scalar(stmt)

        if bad_word:
            session.delete(bad_word)
            return True
        
        return False