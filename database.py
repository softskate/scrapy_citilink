import datetime
import uuid
from peewee import SqliteDatabase, Model, CharField, TextField, \
    UUIDField, DateTimeField, ForeignKeyField, FloatField, BooleanField
from secrets import token_urlsafe
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
# Connect to SQLite database
db = SqliteDatabase(os.path.join(current_dir, 'data.db'), pragmas={'journal_mode': 'wal'}, check_same_thread=False)

class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    name = CharField(unique=True)
    token = CharField(default=token_urlsafe)


class ParsingItem(BaseModel):
    user_id = ForeignKeyField(User)
    link = CharField(unique=True)
    item_type = CharField(20)


class App(BaseModel):
    appid = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField()
    start_url = CharField()


class Crawl(BaseModel):
    crawlid = UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = DateTimeField(default=datetime.datetime.now)


class RawResponseModel(BaseModel):
    appid = ForeignKeyField(App)
    crawlid = ForeignKeyField(Crawl)
    url = TextField()
    statusCode = CharField(max_length=3)
    attrs = TextField(null=True)


class MenuResponseModel(RawResponseModel):
    groupCategoryName = CharField()
    groupName = CharField()
    groupUrl = TextField()


class ProductResponseModel(RawResponseModel):
    groupId = ForeignKeyField(MenuResponseModel, null=True)
    name = CharField()
    productUrl = TextField()
    price = FloatField()


class ProductDetailsResponseModel(RawResponseModel):
    groupId = ForeignKeyField(MenuResponseModel, null=True)
    imageUrls = TextField()
    name = CharField()
    brandName = CharField(null=True)
    description = TextField(null=True)
    details = TextField()
    productUrl = TextField()


if __name__ == "__main__":
    db.connect()
    db.create_tables(BaseModel.__subclasses__()+RawResponseModel.__subclasses__())
    # app = App.create(
    #     name = 'Citilink',
    #     start_url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v2.json'
    # )
    # crawl = Crawl.create()
    # test1 = User.create(name='Dilmurod')
    # test2 = User.create(name='Stas')
    # print(test1.token, test2.token)
# WfkWr3nvA7CSOXFxEBDFUvaxSYGQFTr8xd3Sw1ZMvdM XQ3uvGnDLuc5JtHcLAM3h3XJjbA8xb93bl2659svWVA
