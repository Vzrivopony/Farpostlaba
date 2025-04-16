import random
import datetime
from faker import Faker
import mysql.connector
from mysql.connector import Error
import argparse

# Штука для рандомных данных, прикольно
fake = Faker()

# Подключение к датабазе
db_config = {
    'host': 'localhost',
    'database': 'mydb',
    'user': 'root',
    'password': 'root'  
}

# Справочник действий
ACTION_TYPES = [
    (1, "first_visit"),
    (2, "registration"),
    (3, "login"),
    (4, "logout"),
    (5, "create_thread"),
    (6, "view_thread"),
    (7, "delete_thread"),
    (8, "post_comment")
]

# Справочник ошибок
RESPONSE_TYPES = [
    (1, "success"),
    (2, "error")
]

def create_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def clear_tables(connection):
    cursor = connection.cursor()
    tables = ['actions', 'comments', 'threads', 'users']
    
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
            print(f"Cleared table: {table}")
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        connection.commit()
    except Error as e:
        print(f"Error clearing tables: {e}")
        connection.rollback()
    finally:
        cursor.close()

def populate_lookup_tables(connection):

    cursor = connection.cursor()
    try:
        cursor.executemany(
            "INSERT INTO actions_type (id, name) VALUES (%s, %s)",
            ACTION_TYPES
        )
        
        cursor.executemany(
            "INSERT INTO response_type (id, namer) VALUES (%s, %s)",
            RESPONSE_TYPES
        )
        
        connection.commit()
        print("Populated lookup tables: actions_type and response_type")
    except Error as e:
        print(f"Error populating lookup tables: {e}")
        connection.rollback()
    finally:
        cursor.close()

def generate_users(connection, count=10):
    cursor = connection.cursor()
    try:
        for i in range(1, count + 1):
            login = fake.user_name() + str(i) 
            password = fake.password(length=10)
            cursor.execute(
                "INSERT INTO users (id, login, password) VALUES (%s, %s, %s)",
                (i, login, password)
            )
        connection.commit()
        print(f"Generated {count} users")
    except Error as e:
        print(f"Error generating users: {e}")
        connection.rollback()
    finally:
        cursor.close()

def generate_threads(connection, user_ids, count=10):
    cursor = connection.cursor()
    try:
        for i in range(1, count + 1):
            name = fake.sentence(nb_words=3)[:45]
            user_id = random.choice(user_ids)
            cursor.execute(
                "INSERT INTO threads (id, name, users_id) VALUES (%s, %s, %s)",
                (i, name, user_id)
            )
        connection.commit()
        print(f"Generated {count} threads")
    except Error as e:
        print(f"Error generating threads: {e}")
        connection.rollback()
    finally:
        cursor.close()

def generate_comments(connection, thread_ids, user_ids, count=20):
    cursor = connection.cursor()
    try:
        for i in range(1, count + 1):
            comment = fake.sentence(nb_words=10)[:45]
            thread_id = random.choice(thread_ids)
            cursor.execute(
                "INSERT INTO comments (id, commentscol, threads_id) VALUES (%s, %s, %s)",
                (i, comment, thread_id)
            )
        connection.commit()
        print(f"Generated {count} comments")
    except Error as e:
        print(f"Error generating comments: {e}")
        connection.rollback()
    finally:
        cursor.close()

def generate_actions(connection, user_ids, thread_ids, comment_ids, start_date, end_date):
    cursor = connection.cursor()
    action_id = 1
    
    try:
        delta = end_date - start_date
        days_count = delta.days + 1
        
        for action_type_id, action_name in ACTION_TYPES:
            min_actions_per_day = 5
            if action_type_id == 5:  
                min_actions_per_day = 7  
            
            total_actions = min_actions_per_day * days_count + random.randint(0, 5 * days_count)
            
            for _ in range(total_actions):
                random_day = random.randint(0, days_count - 1)
                action_date = start_date + datetime.timedelta(days=random_day)
                
                action_time = datetime.datetime.combine(
                    action_date,
                    datetime.time(
                        random.randint(0, 23),
                        random.randint(0, 59),
                        random.randint(0, 59)
                    )
                )
                
                user_id = random.choice(user_ids) if random.random() > 0.3 else None
                response_type_id = 1  
                
                if action_type_id == 5:  
                    if action_date in [start_date, end_date] or random.random() < 0.3:
                        user_id = None
                        response_type_id = 2  
                elif action_type_id == 8:  
                    user_id = random.choice(user_ids) if random.random() > 0.5 else None
                    if user_id is None:
                        response_type_id = 2  
                
                thread_id = random.choice(thread_ids) if action_type_id in [5, 6, 7, 8] else None
                comment_id = random.choice(comment_ids) if action_type_id == 8 else None
                
                cursor.execute(
                    """INSERT INTO actions 
                    (id, action_time, users_id, threads_id, comments_id, actions_type_id, response_type_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (action_id, action_time, user_id, thread_id, comment_id, action_type_id, response_type_id)
                )
                action_id += 1
        
        connection.commit()
        print(f"Generated {action_id - 1} actions between {start_date} and {end_date}")
    except Error as e:
        print(f"Error generating actions: {e}")
        connection.rollback()
    finally:
        cursor.close()

def parse_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def main():
    parser = argparse.ArgumentParser(description='Generate forum activity logs')
    parser.add_argument('--start-date', type=parse_date, required=True,
                       help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end-date', type=parse_date, required=True,
                       help='End date in YYYY-MM-DD format')
    
    args = parser.parse_args()
    
    if args.start_date > args.end_date:
        print("Error: Start date must be before end date")
        return
    
    connection = create_db_connection()
    if not connection:
        return
    
    try:
        clear_tables(connection)
        
        populate_lookup_tables(connection)
        
        generate_users(connection, count=10)
        
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        generate_threads(connection, user_ids, count=10)
        
        cursor.execute("SELECT id FROM threads")
        thread_ids = [row[0] for row in cursor.fetchall()]
        
        generate_comments(connection, thread_ids, user_ids, count=20)
        
        cursor.execute("SELECT id FROM comments")
        comment_ids = [row[0] for row in cursor.fetchall()]
        
        generate_actions(connection, user_ids, thread_ids, comment_ids, args.start_date, args.end_date)
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    main()