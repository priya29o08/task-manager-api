from flask import Flask,jsonify,request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

#setting up database
def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS tasks(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   description TEXT,
                   completed INTEGER DEFAULT 0,
                   created_at TEXT
                   )
                   ''')
    conn.commit()
    conn.close()

#initialize database when app start
init_db()

@app.route('/')
def home():
    return jsonify({"messege" : "Task Manager API","status" : "running"})

#create -add new task
@app.route('/tasks',methods= ['POST'])
def create_task():
    data = request.json #user need to give update
    title=data.get('title')
    description=data.get('description','')

    if not title:
        return jsonify({"error" : "Title is required "}) , 400
    conn = sqlite3.connect('tasks.db')
    cursor =conn.cursor()
    cursor.execute('''
    INSERT INTO tasks (title ,description, created_at)
    VALUES  (?,?,?)
    ''',(title, description ,datetime.now().isoformat()))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()

    return jsonify({" message" : "Task created", "id": task_id}),201

#READ -Get all tasks
@app.route('/tasks', methods =['GET'])
def get_tasks():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    cursor= conn.cursor()
    cursor.execute('SELECT * FROM tasks')
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"tasks" : tasks})

#READ - get one task
@app.route('/tasks/<int:id>',methods = ['GET'])
def get_task(id):
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT *FROM tasks WHERE id =?',(id,))
    task=cursor.fetchone()
    conn.close()

    if task:
        return jsonify(dict(task))
    return jsonify({"error" : "Task not found "}),404

#UPDATE - Mark task complete/incomplete 
@app.route('/tasks/<int:id>',methods = ['PUT'])
def update_task(id):
    data = request.json
    completed = data.get('completed',0)

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET completed = ? WHERE id =?',(completed,id))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error" : "Task not found"}), 404
    
    conn.close()
    return jsonify({"message " : "Task updated"})

#Delete - Remove task
@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
    
    conn.close()
    return jsonify({"message": "Task deleted"})

if __name__ == '__main__':
    import os
    port =int(os.environ.get('PORT',5000))
    app.run(host ='0.0.0.0', port= port, debug = True)


