from database import *
from flask import *
import os
from werkzeug import secure_filename
import face_recognition
import cv2
import numpy as np

UPLOAD_FOLDER = 'static/known_people'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def home():
	if request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		phone = request.form['phone']
		photo = request.files['myFile']
		upload_file(photo)
		add_person(name,email,phone,photo.filename)
	return render_template('index.html')

@app.route('/recognition', methods=['GET', 'POST'])
def recognition():
	if request.method =='POST':
		photo = request.files['myFile']
		upload_file(photo)
		path1 = "static/known_people/"+photo.filename
		known_image = face_recognition.load_image_file(path1)
		known_encoding = face_recognition.face_encodings(known_image)[0]
		people = query_all()
		for person in people:
			path = "static/known_people/" + person.picture
			unknown_image = face_recognition.load_image_file(path)
			unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
			results = face_recognition.compare_faces([known_encoding], unknown_encoding)
			if results[0]:
				return render_template('recognise1.html', person=person)
	return render_template('recognise.html')

@app.route('/camera', methods=['GET', 'POST'])
def camera():
	film()
	return redirect(url_for('home'))

def film():
	# Get a reference to webcam #0 (the default one)
	video_capture = cv2.VideoCapture(0)

	# Load a sample picture and learn how to recognize it.
	known_face_encodings=[]
	known_face_names=[]
	for person in query_all():
		path = "static/known_people/"+person.picture
		known_face_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file(path))[0])
		known_face_names.append(person.name)	
	# Initialize some variables
	face_locations = []
	face_encodings = []
	face_names = []
	process_this_frame = True

	while True:
	    # Grab a single frame of video
	    ret, frame = video_capture.read()

	    # Resize frame of video to 1/4 size for faster face recognition processing
	    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

	    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
	    rgb_small_frame = small_frame[:, :, ::-1]

	    # Only process every other frame of video to save time
	    if process_this_frame:
	        # Find all the faces and face encodings in the current frame of video
	        face_locations = face_recognition.face_locations(rgb_small_frame)
	        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

	        face_names = []
	        for face_encoding in face_encodings:
	            # See if the face is a match for the known face(s)
	            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
	            name = "Unknown"

	            # # If a match was found in known_face_encodings, just use the first one.
	            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
	            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
	            best_match_index = np.argmin(face_distances)
	            if matches[best_match_index]:
	                name = known_face_names[best_match_index]

	            face_names.append(name)

	    process_this_frame = not process_this_frame


	    # Display the results
	    for (top, right, bottom, left), name in zip(face_locations, face_names):
	        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
	        top *= 4
	        right *= 4
	        bottom *= 4
	        left *= 4

	        # Draw a box around the face
	        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

	        # Draw a label with a name below the face
	        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
	        font = cv2.FONT_HERSHEY_DUPLEX
	        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

	    # Display the resulting image
	    cv2.imshow('Video', frame)

	    # Hit 'q' on the keyboard to quit!
	    if cv2.waitKey(1) & 0xFF == ord('q'):
	        break

	# Release handle to the webcam
	video_capture.release()
	cv2.destroyAllWindows()

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_file(file):
    if request.method == 'POST':
        if file and allowed_file(file.filename):
#            filename = secure_filename(file.filename)
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
	if request.method == 'POST':
		if request.form['username']=='Face_Recognition' and request.form['pass']=='123456':
			session['admin'] = True
			return redirect(url_for('edit'))
	return render_template('admin.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
	if session['admin']:
		return render_template('edit.html', people = query_all())

@app.route('/edit_person/<int:person_id>', methods=['GET','POST'])
def display_person_edit(person_id):
	if session['admin']:
		person = query_by_id(person_id)
		if request.method == 'POST':
			name = request.form['name']
			email = request.form['email']
			phone = request.form['phone']
			picture = request.files['picture']
			upload_file(picture)
			if name == "":
				name=person.name
			if email == "":
				email=person.email
			if phone == "":
				phone = person.phone
			if picture != None:
				picture1 = picture.filename
			update_person(person_id,name,email,phone,picture1)
			return redirect(url_for('edit'))
		return render_template("edit_project.html", person = person)
	return redirect(url_for('admin'))

@app.route('/delete/<int:person_id>')
def delete_person(person_id):
	if session['admin']:
		delete_by_id(person_id)
		return redirect(url_for('edit'))
	return redirect(url_for('admin'))

@app.route('/logout')
def logout():
	session['admin']=False
	return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

