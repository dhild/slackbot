import os
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from contextlib import contextmanager

DATABASE_URL = os.environ['DATABASE_URL']
engine = create_engine(DATABASE_URL, connect_args={'sslmode': 'require'})
Base = declarative_base()


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    state = Column(String)
    player_location = Column(Integer)
    wumpus_location = Column(Integer)

    def __repr__(self):
        return "<Game(user='%s', state='%s', player_location='%s', wumpus_location='%s', start_time='%s'," \
               " end_time='%s')>" % (
                   self.user_id, self.state, self.player_location, self.wumpus_location, self.start_time, self.end_time)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def find_or_create_game(session, user_id):
    game = session.query(Game).filter(Game.user_id == user_id).one_or_none()
    if game is None:
        game = Game(user_id=user_id, start_time=datetime.now())
        session.add(game)
    return game
