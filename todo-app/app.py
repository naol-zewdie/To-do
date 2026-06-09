from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

tasks = []

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        task_title = request.form.get('task', '').strip()
        if task_title:
            tasks.append({
                'title': task_title,
                'completed': False,
            })
    return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete_task(id):
    if 0 <= id < len(tasks):
        tasks.pop(id)
    return redirect(url_for('home'))

@app.route('/complete/<int:id>')
def complete_task(id):
    if 0 <= id < len(tasks):
        tasks[id]['completed'] = not tasks[id]['completed']
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
