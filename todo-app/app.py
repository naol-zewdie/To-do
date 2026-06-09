from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(10), default='Medium')

    def __repr__(self):
        return f"<Task {self.id}: {self.title!r}>"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        task_title = request.form.get('task', '').strip()
        due_date_str = request.form.get('due_date', '').strip()
        priority = request.form.get('priority', 'Medium')
        due = None
        if due_date_str:
            try:
                due = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                due = None
        if task_title:
            new_task = Task(title=task_title, completed=False, due_date=due, priority=priority)
            db.session.add(new_task)
            db.session.commit()
    filt = request.args.get('filter', 'all')
    q = request.args.get('q', '').strip()
    base = Task.query
    if q:
        base = base.filter(Task.title.ilike(f"%{q}%"))
    if filt == 'completed':
        base = base.filter_by(completed=True)
    elif filt == 'pending':
        base = base.filter_by(completed=False)
    tasks = base.order_by(Task.id).all()
    return render_template('index.html', tasks=tasks, current_filter=filt, search_query=q)

@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get(id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/complete/<int:id>')
def complete_task(id):
    task = Task.query.get(id)
    if task:
        task.completed = not task.completed
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get(id)
    if not task:
        return redirect(url_for('home'))
    if request.method == 'POST':
        title = request.form.get('task', '').strip()
        due_date_str = request.form.get('due_date', '').strip()
        priority = request.form.get('priority', 'Medium')
        if due_date_str:
            try:
                due = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                due = None
        else:
            due = None
        if title:
            task.title = title
            task.due_date = due
            task.priority = priority
            db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', task=task)

def ensure_due_date_column():
    """Add due_date column to existing task table if it's missing (SQLite)."""
    engine = db.get_engine()
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info('task')"))
        cols = [row[1] for row in res.fetchall()]
        if 'due_date' not in cols:
            try:
                conn.execute(text("ALTER TABLE task ADD COLUMN due_date DATE"))
            except Exception:
                pass
        if 'priority' not in cols:
            try:
                conn.execute(text("ALTER TABLE task ADD COLUMN priority VARCHAR(10) DEFAULT 'Medium'"))
            except Exception:
                pass


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_due_date_column()
    app.run(debug=True)
