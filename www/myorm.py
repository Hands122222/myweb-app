# -*- coding:utf-8 -*-#
#!/usr/bin/env python3#

__author__='Hands'
__email__='handssky@foxmail.com'

import asyncio
import logging
import aiomysql


def log(sql,argr=()):
    logging.info('SQL:%s'%sql.join(argr))

@asyncio.coroutine
def create_pool(loop,**kw):
    logging.info('Create data condition pool...')
    global __pool
    __pool= yield from aiomysql.create_pool(
        host=kw.get('host','localhost'),
        port=kw.get('port',3306),
        user=kw.get['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset','utf8'),
        autocommit=kw.get('autocommit',True),
        maxsize=kw.get('maxsize',10),
        minsize=kw.get('minsize',1),
        loop=loop
    )
    print(__pool)

@asyncio.coroutine
def select(sql,argrs,size=None):
    log(sql,argrs)
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        yield from cur.execute(sql.replace('?','%s'),argrs)
        if size:
            rs=yield from cur.fetchmany(size)
        else:
            rs=yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows returned:%d'%len(rs))
        return rs

@asyncio.coroutine
def execute(sql,args):
    log(sql,args)
    with (yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?','%'),args)
            affected = cur.rowcount
            yield from cur.close()
        except BaseException  as e:
            raise
        return affected

#from orm import Model, StringField, IntegerField

r'''class User(Model):
    __table__='users'

    id=IntegerField(primary_key=True)
    naem=StringField()
'''

def create_attr_str(num):
    L=[]
    for x in range(num):
        L.append('?')
    return ','.join(L)

class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<#s,%s:%s>'%(self.__class__.__name__,self.column_type,self.name)

class StringField(Field):
    def __init__(self,name=None,primary_key=False,default=None,ddl='vchar(100)'):
        super().__init__(name,ddl,primary_key,default)

class IntegerField(Field):
    def __init__(self,name=None,priamry_key=False,default=0):
        super().__init__(name,'bigint',priamry_key,default)

class BooleanField(Field):
    def __init__(self,name=None,primary_key=False,default=False):
        super().__init__(name,'boolean',primary_key,default)

class FloatField(Field):
    def __init__(self,name=None,primary_key=False,default=0.0):
        super().__init__(name,'real',primary_key,default)

class TextFiled(Field):
    def __init__(self,name=None,default=None):
        super().__init__(name,'text',False,default)

class ModelMetaclass(type):
    def __new__(cls,name,bases,attr):
        if name == 'Medel':
            return type.__name__(cls,name,bases,attr)

        tableName = attr.get('__table__',None) or name
        logging.info('found model:%s(table:%s)'%(name,tableName))

        mapping = dict()
        fields=[]
        primary_key = None
        for k,v in attr.items():
            if isinstance(v,Field):
                logging.info('found mapping:%s==>%s'%(k,v))
                mapping[k]=v
                if v.primary_key:
                    if primary_key:
                        raise RuntimeError('Duplicate primary key for field: %s'%k)
                    primary_key = k
                else:
                    fields.append(k)
        if not primary_key:
            raise  RuntimeError('Primary key not found')
        for k in mapping.keys():
            attr.pop(k)
        esaped_fileds = list(map(lambda f:'`%s`'%f , fields))
        attr['__mapping__']=mapping
        attr['__table__']=tableName
        attr['__primary_key__']=primary_key
        attr['__fileds__']=fields
        attr['__select__']='select `%s`,%s from `%s`'%(primary_key,','.join(esaped_fileds),tableName)
        attr['__insert__']='insert into `%s` (%s,`%s`) values (`%s)'%(tableName,','.join(esaped_fileds),primary_key,create_attr_str(len(esaped_fileds)+1))
        attr['__delete__']='delete from `%s` where `%s`=?'%(tableName,primary_key)
        attr['__update__']='update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mapping.get(f).name or f), fields)), primary_key)
        return type.__new__(cls,name,bases,attr)

class Model(dict,metaclass=ModelMetaclass):
    def __init__(self,**kw):
        super(Model,self).__init__(**kw)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute:'%s'"%item)

    def __setattr__(self, key, value):
        self[key]=value

    def getValue(self,key):
        return getattr(self,key,None)

    def getValueOrDefault(self,key):
        value = getattr(self,key,None)
        if value is None:
            field = self.__mapping__[key]
            if field.default is not None:
                value = field.default()  if callable(field.default) else field.default
                logging.debug('using default value for %s:%s'%(key,value))
                setattr(self,key,value)
        return value

    @classmethod
    async def findAll(cls,Where=None,args=None,**kw):
        'find object by where clause.'
        sql=[cls.__select__]
        if Where:
            sql.append('where')
            sql.append(Where)
        if args is None:
            args=[]
        orderby = kw.get('orderBy',None)
        if orderby is not None:
            sql.append('order by')
            sql.append(orderby)
        limit = kw.get('limit',None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit,int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit,tuple) and len(limit) == 2:
                sql.append('?,?')
                args.append(limit)
            else:
                raise ValueError('Invalid limit value:%s'%str(limit))

        rs = await setattr(' '.join(sql),args)
        return rs[0]['_num_']

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find(cls,pk):
        ' find objdect by po'
        rs = await setattr('%s where `%s`=?'%(cls.__select__,cls.__primary_key__),pk,1)
        if len(rs)==0:
            return None
        return cls(**rs[0])

    async def save(self):
        args = list(map(self.getValueOrDefault,self.__fileds__))
        args.append(self.getValueOrDefault(self,self.__primary_key__))
        rows = await execute(self.__insert__,args)
        if rows != 1:
            logging.warning('failed to insert record: affected rows:%s'%rows)

    async def update(self):
        args = list(map(self.getValue,self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__,args)
        if rows != 1:
            logging.warning('failed to update  record: affected rows:%s'%rows)

    async def remove(self):
        args= [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__,args)
        if rows!=1:
            logging.warn('failed to remove by primary key: affected rows: %s' % rows)




