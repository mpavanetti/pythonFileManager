# Create by Matheus Pavanetti (matheus.pavanetti@hgv.com)
# Release 1.0.2 - Last Update Date 5/6/2021

#pip3 install flask
#pip3 --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org install flask (In case of SSL Problem)

# Import modules
import os
import glob
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from werkzeug.utils import secure_filename

# Declaring Variables
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10000000000 # MAX 10 GB
app.config['UPLOAD_EXTENSIONS'] = ['.csv','.txt','.xlsx','.xls','.json','.xml','.zip','.sql','.ds','.doc','.docx']

# path variable, using network file share location.
path = "\\\\RSPINDFS01.hgvc.com/corp/"

# App Route, Root , deny access
@app.route("/")
def index():
    return render_template('exception.html')

# App Route /listfiles GET Method, get file name from folder.
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
                return ('No Input filemask. please provide the header name filemask with value.',400)
        else:
            return ('No Input file path. please provide the header name path with value.',400)
    except:
        # Exception, Return HTML Exception template.
        return ('<h1>Exception ALL</h1><br><hr><h3>Some Error Has Occured.</h3>',500)

# App route /getfile/file.txt GET method call
@app.route("/getfile/<string:filename>", methods=["GET"])
def get_files(filename):
    try:
        # Reading Header Values
        inputpath = request.headers.get('path')
        filepath = path + inputpath
        filemask = request.headers.get('filemask')
        foundFile =[]

        # Check path and filemask header values
        if(filename.strip() != ''):
            if(inputpath != None and inputpath.strip() != ''):
                if(filemask != None and filemask.strip() != ''):
                    # Iterating and storing files to variable.
                    files = [os.path.basename(x) for x in glob.glob(filepath + filemask)]
                    # Iterating on files to check if the input filename match with the files found in the folder.
                    for i in files:
                        if(i == filename):
                            foundFile.append(i)
                    if(foundFile):
                        if(foundFile[0] != ''):
                            f = open(filepath+foundFile[0], 'r',encoding='iso-8859-1')
                            final = f.read()
                        else:
                            final = "No File Found"
                    else:
                        final = "No File Found"
                    return final
                else:
                    return ('No Input filemask. please provide the header name filemask with value.',400)    
            else:
                return ('No Input file path. please provide the header name path with value.',400)
        else:
            return ('No inputfilename. please provide the filename to query it.',400)
    except:
        # Exception, Return HTML Exception template.
        return ('<h1>Exception ALL</h1><br><hr><h3>Some Error Has Occured.</h3>',500)

# App route /sendfile POST Method call
@app.route('/sendfile', methods=['POST'])
def upload_files():
    try:
        # Reading Header Values
        inputpath = request.headers.get('path')
        filepath = path + inputpath
      
        # Check for header parameters
        if(inputpath != None and inputpath.strip() != ''):

        # Declare app config
            app.config['UPLOAD_PATH'] = filepath

        # Get uploaded file
            uploaded_file = request.files['file']
            filename = secure_filename(uploaded_file.filename)
            if filename.strip() != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            return "success"
                    
        else:
             return ('No Input file path. please provide the header name path with value.',400)

    except:
       # Exception, Return HTML Exception template.
       return ('<h1>Exception ALL</h1><br><hr><h3>Some Error Has Occured.</h3>',500)
     
# Checks to see if the name of the package is the run as the main package.
if __name__ == "__main__":
    # Runs the Flask application only if the main.py file is being run.
    app.run()