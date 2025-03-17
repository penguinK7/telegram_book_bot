from db_handler.database import database
from db_handler.models import User, Book, Vote

# создала файл чтобы после изменения в моделях чистить базы запуском
def reset_database():
    database.connect()
    database.drop_tables([User, Book, Vote], safe=True)
    database.create_tables([User, Book, Vote], safe=True)
    database.close()

if __name__ == "__main__":
    reset_database()
    print("База данных успешно очищена и создана заново.")
