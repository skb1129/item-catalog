from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Users(Base):
	__tablename__ = 'users'

	email = Column(String(80), primary_key = True)
	name = Column(String(80), nullable = False)
	picture = Column(String(80))


class Genres(Base):
	__tablename__ = 'genres'

	name = Column(String(80), primary_key = True)
	user_email = Column(String(80), ForeignKey('users.email'))
	users = relationship(Users)


	@property
	def serialize(self):
		"""Return object data for json file."""
		return {
			'name': self.name
		}


class Movies(Base):
	__tablename__ = 'movies'

	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	director = Column(String(80), nullable = False)
	description = Column(Text)
	posterUrl = Column(String(80))
	genre = Column(String(80), ForeignKey('genres.name'))
	genres = relationship(Genres)
	user_email = Column(String(80), ForeignKey('users.email'))
	users = relationship(Users)


	@property
	def serialize(self):
		"""Return object data for json file."""
		return {
			'id': self.id,
			'name': self.name,
			'posterUrl': self.posterUrl,
			'director': self.director,
			'description': self.description,
			'genre': self.genre
		}


engine = create_engine('sqlite:///movies.db')

Base.metadata.create_all(engine)
