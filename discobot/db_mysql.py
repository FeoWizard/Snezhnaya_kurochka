#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import threading

import time
import datetime
import log_module
import pymysql

import aiomysql

from sshtunnel  import SSHTunnelForwarder
from bot_config import BOT_NAME, CONNECTION_MIN_COUNT, CONNECTION_MAX_COUNT
from bot_enums  import UserDialogState, CommentEntities

logger    = log_module.Logger_Factory(BOT_NAME).get_logger("MySQL_logger")
localhost = "127.0.0.1"

# noinspection PyArgumentList,PyMethodMayBeStatic
class MySQLAsyncWorker:
    __pool       = None
    __loop       = None
    __ssh_server = None

    def __get_event_loop(self, loop):
        try:
            # Если запущенный цикл уже есть, то хватаем его
            loop = asyncio.get_running_loop()

        except RuntimeError:
            # Если нет запущенного цикла, проверяем, есть ли цикл, переданный в аргументе
            # Если нет, то создаём новый цикл событий
            if (not loop):
                loop = asyncio.new_event_loop()

        return loop

    def __init__(self, host: str, port: int, user: str, password: str, db_name: str, echo: bool, autocommit: bool,
                 ssh_ip:      str = None, ssh_port:      int = None, ssh_login: str = None, ssh_pass: str = None,
                 ssh_bind_ip: str = None, ssh_bind_port: int = None, loop = None):

        loop = self.__get_event_loop(loop)

        # Запускаем задачу создания пула соединений в цикле событий
        loop.run_until_complete(self.__worker_init(host, port, user, password, db_name, echo, autocommit,
                                                   ssh_ip, ssh_port, ssh_login, ssh_pass, ssh_bind_ip, ssh_bind_port))

    @staticmethod
    def __create_ssh_link(ssh_ip, ssh_port, ssh_username, ssh_password, bind_ip, bind_port):
        server = SSHTunnelForwarder(
            (ssh_ip, ssh_port),
            ssh_username = ssh_username,
            ssh_password = ssh_password,
            remote_bind_address = (bind_ip, bind_port))
        server.daemon_forward_servers = True
        server.daemon_transport       = True
        return server


    async def __worker_init(self, host: str, port: int, user: str, password: str, db_name: str, echo: bool, autocommit: bool,
                            ssh_ip:  str = None, ssh_port:  int = None, ssh_login: str = None, ssh_pass: str = None,
                            bind_ip: str = None, bind_port: int = None):
        if (ssh_ip is None):
            host = host
            port = port
        else:
            self.__ssh_server = self.__create_ssh_link(ssh_ip, ssh_port, ssh_login, ssh_pass, bind_ip, bind_port)
            self.__ssh_server.start()
            logger.info(msg = "SSH Link established")
            host = self.__ssh_server.local_bind_host
            port = self.__ssh_server.local_bind_port

        try:
            self.__loop = asyncio.get_event_loop()
            self.__pool = await aiomysql.create_pool(host    = host,    port       = port,
                                                     user    = user,    password   = password,
                                                     db      = db_name, loop    = self.__loop,
                                                     echo    = echo,    autocommit = autocommit,
                                                     minsize = CONNECTION_MIN_COUNT,
                                                     maxsize = CONNECTION_MAX_COUNT)
            logger.info(msg = "MYSQL Connection_pool created")
        except BaseException as err:
            logger.critical(msg = "Error during Connection_pool creating!", exc_info = err)

    def ssh_close(self):
        if (self.__ssh_server):
            self.__ssh_server.close()
            logger.info(msg = "SSH Link closed")

    def close(self):
        asyncio.get_event_loop().run_until_complete(self.__close())

    async def __close(self):
        self.__pool.close()
        await self.__pool.wait_closed()
        logger.info(msg = "MYSQL Connection_pool closed")

    async def conn_count(self):
        return self.__pool.size

    async def free_conn_count(self):
        return self.__pool.freesize

    async def conn_reset(self):
        try:
            await self.__pool.clear()
            logger.info(msg = "Connection pool reset done successfully")
        except BaseException as err:
            logger.error(msg = "Error during connections reset!", exc_info = err)

    # noinspection PyMethodParameters
    def db_error_catcher(method_to_decorate):
        # noinspection PyCallingNonCallable
        async def wrapper(*args, **kwargs):
            self = args[0]
            try:
                result = await method_to_decorate(*args, **kwargs)

                # if (result):
                #     logger.debug(msg = "Queue result: \n{}".format(result))

                return result
            # Здесь возвращается либо True, либо None - в случае, если ничего не найдено
            except BaseException as error:
                logger.error(msg = "\n\nSQL QUEUE:\n{}".format(args[1]))
                logger.error(msg = "Database error:\n\n", exc_info = error)
                return False
                # Если произошла ошибка - возвращаем False

        return wrapper

    @db_error_catcher
    async def __start_database_query(self, sql_stmt: str, args: list = None):

        while (self.__pool is None):
            await asyncio.sleep(0.05)

        conn   = await self.__pool.acquire()
        cursor = await conn.cursor(aiomysql.DictCursor)
        if (args is None):
            result = await cursor.execute(sql_stmt)

        else:
            result = await cursor.execute(sql_stmt, args)

        if ("INSERT" in sql_stmt):
            sql_stmt = "SELECT LAST_INSERT_ID() as 'last_id';"
            result = await cursor.execute(sql_stmt)

        await self.__pool.release(conn)
        result = await cursor.fetchall()
        await cursor.close()

        if (result):
            # Если в результате один элемент, то отдаём его
            if (len(result) == 1):
                return result[0]

            logger.debug(msg = "Queue successful")
            return result
        else:
            logger.debug(msg = "Queue successful, but result is None")
            return None

    async def DEV_check_base(self):
        sql_stmt = "SELECT 1"
        return await self.__start_database_query(sql_stmt)