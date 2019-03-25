import os
from sqlalchemy.orm import sessionmaker, relationship, selectinload
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, and_
from contextlib import contextmanager
import app.wumpus.hunt

DATABASE_URL = os.environ['DATABASE_URL']
engine = create_engine(DATABASE_URL, connect_args={'sslmode': 'require'})
Base = declarative_base()


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    channel_id = Column(String)
    start_time = Column(DateTime)
    state = Column(Integer)
    player_location = Column(Integer)
    wumpus_location = Column(Integer)
    arrows = Column(Integer)

    def __repr__(self):
        return "<Game(user='%s', state='%s', player_location='%s', wumpus_location='%s')>" % (
            self.user_id, self.state, self.player_location, self.wumpus_location)


class Pit(Base):
    __tablename__ = "pits"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    location = Column(Integer)

    game = relationship("Game", back_populates="pits")

    def __repr__(self):
        return "<Pit(location='%s')>" % self.location


Game.pits = relationship("Pit", order_by=Pit.id, back_populates="game", cascade="all, delete, delete-orphan")


class Bat(Base):
    __tablename__ = "bats"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    location = Column(Integer)

    game = relationship("Game", back_populates="bats")

    def __repr__(self):
        return "<Bat(location='%s')>" % self.location


Game.bats = relationship("Bat", order_by=Bat.id, back_populates="game", cascade="all, delete, delete-orphan")

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


def does_game_exist(session, user_id, channel_id):
    game = session.query(Game). \
        options(selectinload(Game.pits)). \
        options(selectinload(Game.bats)). \
        filter(and_(Game.user_id == user_id, Game.channel_id == channel_id)). \
        one_or_none()
    return game is not None


def find_game(session, user_id, game_id):
    game = session.query(Game). \
        options(selectinload(Game.pits)). \
        options(selectinload(Game.bats)). \
        filter(and_(Game.user_id == user_id, Game.id == game_id)). \
        one_or_none()
    if game is None:
        return
    bat_locations = map(lambda x: x.location, game.bats)
    pit_locations = map(lambda x: x.location, game.pits)
    wh = app.wumpus.hunt.Game(username=user_id, player_location=game.player_location,
                              wumpus_location=game.wumpus_location, bat_locations=bat_locations,
                              pit_locations=pit_locations, arrows=game.arrows)
    wh.db_game = game
    return wh


def save_game(session, game):
    if not game.should_continue():
        session.delete(game.db_game)
        return

    if not hasattr(game, 'db_game'):
        g = Game(user_id=game.username)
        session.add(g)
        game.db_game = g

    game.db_game.arrows = game.arrows
    game.db_game.player_location = game.player_location
    game.db_game.wumpus_location = game.wumpus_location
    game.db_game.arrows = game.arrows
