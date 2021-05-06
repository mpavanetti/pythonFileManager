#main.py
#pip3 install flask
#pip3 --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org install flask (In case of SSL Problem)

# Import modules
import os
import glob
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from werkzeug.utils import secure_filename

# Declaring Variables
path = "\\\\RSPINDFS01.hgvc.com/corp/"
inbound ="input\//"
extension = "*.csv"

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.csv','.txt']
app.config['UPLOAD_PATH'] = path+inbound

@app.route("/")
def index():
    return render_template('exception.html')

@app.route("/listfiles", methods=["GET"])
def list_files():
    try:
        # Reading Header Values
        inputpath = request.headers.get('path')
        filepath = path + inputpath
        filemask = request.headers.get('filemask')

        # Check path and filemask header values
        if(inputpath != None and inputpath.strip() != ''):
            if(filemask != None and filemask.strip() != ''):
                # Iterating and storing files to variable
                files = [os.path.basename(x) for x in glob.glob(filepath + filemask)]
                # Return files (String)
                return str(files)
            else:
                return "No Input filemask. please provide the header name filemask with value."    
        else:
            return "No Input file path. please provide the header name path with value."

    except:

        # Exception, Return HTML Exception template.
        return "<h1>Exception ALL</h1><br><hr><h3>Some Error Has Occured.</h3>"

@app.route("/getfile/<string:filename>", methods=["GET"])
def get_files(filename):
    try:
        foundFile =[]
        files = [os.path.basename(x) for x in glob.glob(path + extension)]
        if(filename == "" or filename == " "):
                result = "No File Found, type a valid fileName."
        else:
            for i in files:
                if(i == filename):
                    foundFile.append(i)
            if(foundFile):
                if(foundFile[0] != ''):
                    f = open(path+foundFile[0], 'r',encoding='iso-8859-1')
                    final = f.read()
                else:
                    final = "No File Found"
            else:
                final = "No File Found"
            return final
    except:
        return "<h1>Exception ALL</h1><br><hr><h3>Some Error Has Occured.</h3>"

@app.route('/sendfile', methods=['POST'])
def upload_files():
    try:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
               abort(400)
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        return "success"
    except:
       return "<h1>Exception ALL</h1><br><hr><h3>Some Error Has Occured.</h3>",400
     
# Checks to see if the name of the package is the run as the main package.
if __name__ == "__main__":
    # Runs the Flask application only if the main.py file is being run.
    app.run()