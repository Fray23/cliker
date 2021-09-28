import datetime
import logging
import psycopg2
import psycopg2.extras
from utils import Status
from settings import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST


# Singleton pattern
class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DataBase(object):
    __metaclass__ = SingletonMeta

    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user=user
        self.password=password
        self.host=host
        self.conn = None

    def open_connection(self):
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    dbname='inst', 
                    user='python', 
                    password='python', 
                    host='localhost'
                )
            except psycopg2.DatabaseError as e:
                logging.error('Database connect error', e)
            finally:
                logging.debug('connection to databse is successful')

    # create tables
    def migrate(self):
        with self.conn.cursor() as cur:
            with open("migrate.sql", "r") as migrate_file:
                cur.execute(migrate_file.read())
            self.conn.commit()



db = DataBase(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
db.open_connection()
db.migrate()


class TaskGRUD:
    @staticmethod
    def create(profile, number_of_posts, hostname):
        dt = datetime.datetime.now()

        with db.conn.cursor() as cur:
            cur.execute(
                'INSERT INTO tasks (profile, number_of_posts, hostname, created_on, status) \
                VALUES (%s, %s, %s, %s, %s)', 
                (profile, number_of_posts, hostname, dt, Status.NEW)
                )
            db.conn.commit()

    @staticmethod
    def get_first_new_tasks():
        with db.conn.cursor() as cur: 
            cur.execute(
                "SELECT * FROM tasks WHERE status = %s ORDER BY task_id ASC LIMIT 1;",
                (Status.NEW,)
                )
            task = cur.fetchone()
            db.conn.commit()
        return task

    @staticmethod
    def update_to_take_to_work(task_id):
        dt = datetime.datetime.now()

        with db.conn.cursor() as cur: 
            cur.execute(
                "UPDATE tasks set status = %s, time_taking_to_work = %s WHERE task_id = %s",
                (Status.IN_WORK, dt, task_id)
                )
            db.conn.commit()

    @staticmethod
    def update_to_finish(task_id):
        dt = datetime.datetime.now()

        with db.conn.cursor() as cur: 
            cur.execute(
                "UPDATE tasks set status = %s, time_finish = %s WHERE task_id = %s",
                (Status.FINISHED, dt, task_id)
                )
            db.conn.commit()

    @staticmethod
    def update_to_log_error(task_id):
        dt = datetime.datetime.now()

        with db.conn.cursor() as cur: 
            cur.execute(
                "UPDATE tasks set status = %s, time_finish = %s WHERE task_id = %s",
                (Status.ERROR, dt, task_id)
                )
            db.conn.commit()



    @staticmethod
    def get_tasks_by_status(status):
        tasks = None

        with db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: 
            cur.execute(
                "SELECT * FROM tasks WHERE status = %s;",
                (status,)
                )
            tasks = cur.fetchall()
            db.conn.commit()
        return tasks

    #
    # analitics query
    #

    @staticmethod
    def get_tasks_count_on_hosts():
        analitics = None

        with db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: 
            cur.execute(
                "select hostname, COUNT(task_id) from tasks group by hostname;"
                )   
            analitics = cur.fetchall()
            db.conn.commit()
        return analitics

    # average timedelta (created_on, time_finish)
    @staticmethod
    def average_timedelta_created_finish():
        analitics = None

        with db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: 
            cur.execute(
                "select AVG(time_finish - created_on) from tasks where status='finished';"
                )   
            analitics = cur.fetchall()
            db.conn.commit()
        return analitics

    # average timedelta (created_on, time_taking_to_work)
    @staticmethod
    def average_timedelta_created_taking_to_work():
        analitics = None

        with db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: 
            cur.execute(
                "select AVG(time_taking_to_work - created_on) from tasks where status='finished';"
                )   
            analitics = cur.fetchall()
            db.conn.commit()
        return analitics

    # the number of tasks for each  hostname with a task creation in last 3 hours
    @staticmethod
    def task_count_3_hours_interval():
        with db.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur: 
            cur.execute(
                "select hostname, COUNT(task_id) from tasks where created_on BETWEEN %s and %s group by hostname;",
                (datetime.datetime.now() - datetime.timedelta(hours=3), datetime.datetime.now())
                )
            analitics = cur.fetchall()
            db.conn.commit()
        return analitics


class PostGRUD:
    @staticmethod
    def create_post_info(post_url, number_of_likes, post_created_on):
        with db.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO posts (post_url, number_of_likes, post_created_on) \
                VALUES (%s, %s, %s)",
                (post_url, number_of_likes, post_created_on)
                )
            db.conn.commit()
