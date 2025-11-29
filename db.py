
import mysql.connector
from mysql.connector import IntegrityError, Error

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Harakumar@999",
        database="student_marks_db"
    )

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        roll VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(255),
        class_name VARCHAR(100),
        math INT DEFAULT 0,
        science INT DEFAULT 0,
        english INT DEFAULT 0,
        total INT DEFAULT 0,
        average FLOAT DEFAULT 0,
        grade VARCHAR(5)
    ) ENGINE=InnoDB;
    """)
    conn.commit()
    cur.close()
    conn.close()

def add_student(roll, name, class_name, math, science, english):
    total = (math or 0) + (science or 0) + (english or 0)
    average = total / 3.0
    grade = calculate_grade(average)
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO students
               (roll, name, class_name, math, science, english, total, average, grade)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (roll, name, class_name, math, science, english, total, average, grade)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True, None
    except IntegrityError as e:
        return False, str(e)
    except Error as e:
        return False, str(e)

def update_student(student_id, roll, name, class_name, math, science, english):
    total = (math or 0) + (science or 0) + (english or 0)
    average = total / 3.0
    grade = calculate_grade(average)
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """UPDATE students SET roll=%s, name=%s, class_name=%s, math=%s, science=%s, english=%s,
                   total=%s, average=%s, grade=%s WHERE id=%s
            """,
            (roll, name, class_name, math, science, english, total, average, grade, student_id)
        )
        conn.commit()
        affected = cur.rowcount
        cur.close()
        conn.close()
        return affected > 0
    except IntegrityError:
        return False
    except Error:
        return False

def delete_student(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM students WHERE id=%s', (student_id,))
    conn.commit()
    cur.close()
    conn.close()

def fetch_all(order_by='id'):
    conn = get_connection()
    cur = conn.cursor()
    # sanitize order_by: allow only certain columns
    allowed = {'id','roll','name','class_name','math','science','english','total','average','grade'}
    if order_by not in allowed:
        order_by = 'id'
    cur.execute(f'SELECT id, roll, name, class_name, math, science, english, total, average, grade FROM students ORDER BY {order_by}')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def search(term):
    t = f'%%{term}%%'
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, roll, name, class_name, math, science, english, total, average, grade FROM students WHERE roll LIKE %s OR name LIKE %s OR class_name LIKE %s ORDER BY id', (t,t,t))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# small helper (kept in db.py for convenience)
def calculate_grade(avg):
    try:
        a = float(avg)
    except Exception:
        return ''
    if a >= 90:
        return 'A'
    if a >= 80:
        return 'B'
    if a >= 70:
        return 'C'
    if a >= 60:
        return 'D'
    return 'F'
