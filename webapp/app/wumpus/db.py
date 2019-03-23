import os
from sqlalchemy.orm import sessionmaker, relationship, selectinload
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
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
    state = Column(Integer)
    player_location = Column(Integer)
    wumpus_location = Column(Integer)
    arrows = Column(Integer)

    def __repr__(self):
        return "<Game(user='%s', state='%s', player_location='%s', wumpus_location='%s', start_time='%s'," \
               " end_time='%s')>" % (
                   self.user_id, self.state, self.player_location, self.wumpus_location, self.start_time, self.end_time)


class Pit(Base):
    __tablename__ = "pits"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    location = Column(Integer)

    game = relationship("Game", back_populates="pits")

    def __repr__(self):
        return "<Pit(location='%s')>" % self.location


Game.pits = relationship("Pit", order_by=Pit.id, back_populates="game")


class Bat(Base):
    __tablename__ = "bats"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    location = Column(Integer)

    game = relationship("Game", back_populates="bats")

    def __repr__(self):
        return "<Bat(location='%s')>" % self.location


Game.bats = relationship("Bat", order_by=Bat.id, back_populates="game")

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


def find_game(session, user_id):
    return session.query(Game). \
        options(selectinload(Game.pits)). \
        options(selectinload(Game.bats)). \
        filter(Game.user_id == user_id). \
        one_or_none()
