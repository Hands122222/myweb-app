import asyncio
from www import orm
from www.models import User, Blog, Comment

async def test(loop):
    await  orm.create_pool(loop,user='www-data', password='www-data', database='awesome')
    u = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
#    User.findAll()
    print(u)
    await u.save()
    print(u.id)

loop=asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()