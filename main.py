# Create by Matheus Pavanetti (matheus.pavanetti@hgv.com)
# Release 1.0.2 - Last Update Date 5/6/2021

#pip3 install flask
#pip3 --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org install flask (In case of SSL Problem)

# Import modules
import os
import glob
import shutil
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

# App route /movefiles POST Method call
@app.route('/movefiles', methods=['POST'])
def move_files():
    try:
         # Reading Header Values
        sourcePath = request.headers.get('sourcePath')
        sourceFilePath = path + sourcePath
        targetPath = request.headers.get('targetPath')
        targetFilePath = path + targetPath
        filemask = request.headers.get('filemask')

        # Check for header parameters
        if(sourcePath != None and sourcePath.strip() != ''):
            if(targetPath != None and targetPath.strip() != ''):
                if(filemask != None and filemask.strip() != ''):

                    files = [os.path.basename(x) for x in glob.glob(sourceFilePath + filemask)]
                    for i in files:
                        original =  sourceFilePath + i
                        target =  targetFilePath + i
                        print("original"+original)
                        print("target"+target)
                        shutil.move(original,target)

                    return 'success'
                else:
                 return ('No filemask, please input on header the filemask name and value',400)   
            else:
             return ('No Target File Path, please input on header the targetPath name and value',400)   
        else:
            return ('No Source File Path, please input on header the sourcePath name and value',400)
        
    except:
       # Exception, Return HTML Exception template.
       return ('<h1>Exception ALL</h1><br><hr><h3>Some Error Has Occured.</h3>',500)

# App route /renamefile PUT Method call
@app.route('/renamefile', methods=['PUT'])
def rename_file():
    try:
        # Reading Header Values
        sourceFile = request.headers.get('sourceFile')
        sourceFilePath = path + sourceFile
        targetFile = request.headers.get('targetFile')
        targetFilePath = path + targetFile

        # Check for header parameters
        if(sourceFile != None and sourceFile.strip() != ''):
            if(targetFile != None and targetFile.strip() != ''):
                # Check if the Source file exist
                if(os.path.exists(sourceFilePath)):
                    # Rename File using suthil move method    
                    shutil.move(sourceFilePath,targetFilePath)
                    return 'success' 
                else:
                    return 'No File Exist',400
            else:
             return ('No Target File Path, please input on header the targetPath name and value',400)   
        else:
            return ('No Source File Path, please input on header the sourcePath name and value',400)
        
    except:
       # Exception, Return HTML Exception template.
       return ('<h1>Exception ALL</h1><br><hr><h3>Some Error Has Occured.</h3>',500)

# App route /deletefile PUT Method call
@app.route('/deletefile', methods=['DELETE'])
def delete_file():
    try:
        # Reading Header Values
        file = request.headers.get('file')
        filePath = path + file

        # Check for header parameters
        if(file != None and file.strip() != ''):
                # Check if the Source file exist
                if(os.path.exists(filePath)):
                    # Rename File using suthil move method    
                    os.remove(filePath)
                    return 'success' 
                else:
                    return 'No File Exist',400 
        else:
            return ('No Source File Path, please input on header the sourcePath name and value',400)
        
    except:
       # Exception, Return HTML Exception template.
       return ('<h1>Exception ALL</h1><br><hr><h3>Some Error Has Occured.</h3>',500)

# Checks to see if the name of the package is the run as the main package.
if __name__ == "__main__":
    # Runs the Flask application only if the main.py file is being run.
    app.run()