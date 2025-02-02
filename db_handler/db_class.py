from db_handler.database import database 

# Создание таблиц
def create_tables():    
    from db_handler.models import User, Book, Vote
    database.connect()
    database.create_tables([User, Book, Vote], safe=True)
    database.close()