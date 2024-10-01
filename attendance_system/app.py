from flask import Flask, render_template, request, send_from_directory
import subprocess

app = Flask(__name__)


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def home():
    return render_template('index.html', static_url='/static')

@app.route('/add_user', methods=['POST'])
def add_user():
    
    name = request.form['name']
    photo = request.files['photo']

   
    photo.save(f'Images/{name}.jpg')

    return '', 204 

@app.route('/take_attendance', methods=['GET'])
def take_attendance():
    
    subprocess.run(['python', 'Attendance/Attendance.py'])

    return '', 204  

if __name__ == '__main__':
    app.run(debug=True)
