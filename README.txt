
Student Marks Management System (MySQL)
--------------------------------------

Files:
- main.py        : Entry point (runs the Tkinter app)
- db.py          : MySQL connection and CRUD operations
- ui.py          : Tkinter GUI that calls db.py functions
- requirements.txt: required Python packages

Setup:
1. Install dependencies:
   pip install -r requirements.txt

2. Ensure MySQL server is running and the database 'student_marks_db' exists.
   If it doesn't exist, create it:
     - mysql -u root -p
     - CREATE DATABASE student_marks_db;

3. Run the app:
   python main.py

Notes:
- Credentials are already placed in db.py (host, user, password, database) as you provided.
- For production, consider moving credentials to environment variables.
