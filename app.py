from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Video
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'your_secret_key'

# Initialize db with app
db.init_app(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    videos = Video.query.all()
    return render_template('home.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            new_video = Video(filename=filename)
            db.session.add(new_video)
            db.session.commit()

            flash("Video uploaded successfully!")
            return redirect(url_for('home'))
        else:
            flash("File type not allowed")
            return redirect(request.url)

    return render_template('upload.html')

# Route to delete a video by ID
@app.route('/delete_video/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    
    # Delete the video file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete the video record from the database
    db.session.delete(video)
    db.session.commit()
    
    flash("Video deleted successfully!")
    return redirect(url_for('home'))

@app.route('/emotion_quiz')
def emotion_quiz():
    return render_template('emotion_quiz.html')

@app.route('/process_emotion_quiz', methods=['POST'])
def process_emotion_quiz():
    # Get the emotion choice from the form
    emotion = request.form.get('emotion')
    
    # Here, you can add logic based on the selected emotion
    flash(f"You selected: {emotion}")
    
    # Redirect back to the home page or display a results page
    return redirect(url_for('home'))



# Initialize database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
