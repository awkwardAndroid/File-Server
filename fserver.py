import os
import pathlib
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

# I use this port to be able to access this server from another device
PORT = 8080 
HOST = "0.0.0.0"

# Get the current path location
current_path = pathlib.Path(__file__).parent.resolve()

# Add or remove allowed file types as you wish
# these are somewhat catogorized so its easier to find the files on the website
# put random or uncategorized extensions in OTHER_EXTENSIONS
IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".tiff"]
EBOOK_EXTENSIONS = [".epub", ".pdf", ".mobi", ".azw", ".azw3"]
DOCUMENT_EXTENSIONS = [".doc", ".docx", ".txt"]
VIDEO_EXTENSIONS = [".mp4", ".mov", ".mkv", ".avi"]
AUDIO_EXTENSIONS = [".mp3", ".wav", ".m4a", ".flac", ".aac"]
OTHER_EXTENSIONS = [".py"]
ALL_EXTENSIONS = [IMAGE_EXTENSIONS, EBOOK_EXTENSIONS, DOCUMENT_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS, OTHER_EXTENSIONS]

ALLOWED_EXTENSIONS = []
# Go trough all extensions
for extensions in ALL_EXTENSIONS:
    # Reset temp variable
    temp = []
    # create a copy of the array so you won't affect the original array
    temp = extensions.copy()
    if temp != []:
        for end in temp:
            end = end.replace(".", "")
            print("[+] Adding extensions: ", end)
            ALLOWED_EXTENSIONS.append(end)
# Folder where the files are
UPLOAD_FOLDER = "files"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "ff0000"

app.add_url_rule(
    "/download/<name>", endpoint="download_file"
)

# Function to check if a file being uploaded is in allowed extensions
def allowed_file(filename):
    if "." not in filename: # If no extension in filename
        flash("Filename doesnt have an extension")
        return False
    temp = filename.rsplit('.',1)[1].lower()

    is_true = False
    if temp in ALLOWED_EXTENSIONS:
        is_true = True
    return is_true

def in_category(item, category_list):
    if item in category_list:
        return True
    else:
        return False

@app.route("/",methods=['GET','POST'])
def index():
    all_files = os.listdir(UPLOAD_FOLDER)
    # file categories
    images = []
    ebooks = []
    documents = []
    videos = []
    audios = []
    others = []
    
    for item in all_files:
        # save the file extension into temp variable
        file_end = os.path.splitext(item)[1]
        # Check file extension and add to the right category
        if in_category(file_end, IMAGE_EXTENSIONS):
            images.append(item)
        elif in_category(file_end, EBOOK_EXTENSIONS):
            ebooks.append(item)
        elif in_category(file_end, DOCUMENT_EXTENSIONS):
            documents.append(item)
        elif in_category(file_end, VIDEO_EXTENSIONS):
            videos.append(item)
        elif in_category(file_end, AUDIO_EXTENSIONS):
            audios.append(item)
        else:
            others.append(item)

    # File upload
    if request.method == "POST":
        if 'file' not in request.files:
            flash("no file part")
            return redirect(request.url)
        file = request.files['file']
        print(file.filename)
        # Check if there is no selected file
        if file.filename == '':
            flash("no selected file")
            return redirect(request.url)
        # Check for file and if in allowed extensions
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # if this redirect is not here, you won't see the file on the website without refreshing
            return redirect(url_for('index'))

    return render_template("index.html", images=images, ebooks=ebooks, documents=documents, videos=videos, audios=audios, others=others)

@app.route('/download/<name>')
def download_file(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'],name)

@app.route('/delete/<name>')
def delete_file(name):
    file = os.path.join(app.config['UPLOAD_FOLDER'],name)
    try:
        if os.path.isfile(file):
            os.remove(file)
    except FileNotFoundError as e:
        print("File doesnt exist error: ", e)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
