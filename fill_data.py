from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Users, Genres, Movies

engine = create_engine('sqlite:///movies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
Session = DBSession()

user = Users(email='skb291129@gmail.com',
				name='Surya Kant Bansal',
				picture='https://lh3.googleusercontent.com/-g-KAax0CVjY/AAAAAAAAAAI/AAAAAAAAAIM/LxKQYnUrLYk/photo.jpg')

Session.add(user)

genre = Genres(name='Horror',
				user_email='skb291129@gmail.com')

Session.add(genre)

genre = Genres(name='Comedy',
				user_email='skb291129@gmail.com')

Session.add(genre)

genre = Genres(name='Action',
				user_email='skb291129@gmail.com')

Session.add(genre)

genre = Genres(name='Drama',
				user_email='skb291129@gmail.com')

Session.add(genre)

movie = Movies(name='Insidious',
				director='James Wan',
				description='Josh and Renai Lambert, along with their three children, move into a new house. While Josh is exploring the attic one night he falls down and slips into a coma.',
				posterUrl='https://t1.gstatic.com/images?q=tbn:ANd9GcTMEANdYRErlG5ciJT1yil85GEsxPyzMRpo4zaiKqhcGOfcxQfC',
				genre='Horror',
				user_email='skb291129@gmail.com')

Session.add(movie)

movie = Movies(name='21 Jump Street',
				director='Phil Lord, Chris Miller',
				description='Schmidt and Jenko are high school friends who go onto become police officers. The two rookie cops go undercover as students in order to bust a drug ring and find the source of a synthetic drug.',
				posterUrl='https://t3.gstatic.com/images?q=tbn:ANd9GcRLCqM8Ispa4waG8tNLPdy6rtiJFOEZUZxdzP-y_BQzfgo953Gb',
				genre='Comedy',
				user_email='skb291129@gmail.com')

Session.add(movie)

movie = Movies(name='Cast Away',
				director='Robert Zemeckis',
				description='Chuck Noland wakes up on a deserted island after his plane crash-lands in the Pacific. He must harness every skill he knows to survive the mental and physical agony of living alone.',
				posterUrl='https://www.gstatic.com/tv/thumb/movieposters/26553/p26553_p_v8_at.jpg',
				genre='Drama',
				user_email='skb291129@gmail.com')

Session.add(movie)

movie = Movies(name='The Hitman\'s Bodyguard',
				director='Patrick Hughes',
				description='The world\'s top protection agent is called upon to guard the life of his mortal enemy, one of the world\'s most notorious hit men. The relentless bodyguard and manipulative assassin have been on the opposite end of the bullet for years and are thrown together for a wildly outrageous 24 hours. During their journey from England to the Hague, they encounter high-speed car chases, outlandish boat escapades and a merciless Eastern European dictator who is out for blood.',
				posterUrl='https://t3.gstatic.com/images?q=tbn:ANd9GcRp9f9X9bK3mxhMNxYTXbjSx7WlFmG3gEYQjK8bS7xncQJFpqVt',
				genre='Action',
				user_email='skb291129@gmail.com')

Session.add(movie)
Session.commit()