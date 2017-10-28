from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Users, Genres, Movies

engine = create_engine('sqlite:///movies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
Session = DBSession()


genre = Genres(name='Action')
Session.add(genre)
Session.commit()

genre = Genres(name='Adventure')
Session.add(genre)
Session.commit()

genre = Genres(name='Horror')
Session.add(genre)
Session.commit()

genre = Genres(name='Drama')
Session.add(genre)
Session.commit()
