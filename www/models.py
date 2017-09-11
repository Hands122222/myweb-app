import time,uuid

from orm import Model,StringField, BooleanField, FloatField, TextField
def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__='users'
    id = StringField(primary_key=True,default=next_id(),ddl='varchar(50)',name='id')
    email = StringField(ddl='varchar(50)',name='email')
    password = StringField(ddl='varchar(50)',name='password')
    admin = BooleanField(name='admin')
    name = StringField(name='name',ddl='varchar(50)')
    image = StringField(name='image',ddl='varchar(500)')
    created_at = FloatField(name='created_at',default = time.time())

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)

class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)




