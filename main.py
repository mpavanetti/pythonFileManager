# Create by Matheus Pavanetti (matheuspavanetti@gmail.com)
# Release 1.0.4 - Last Update Date 5/7/2021

# Import modules
import os
import time
import glob
import shutil
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import jwt
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Declaring Variables
app = Flask(__name__)
app.config['SECRET_KEY'] = 'The lazy fox has jumped in the river'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['MAX_CONTENT_LENGTH'] = 10000000000 # MAX 10 GB
app.config['UPLOAD_EXTENSIONS'] = ['.csv','.txt','.xlsx','.xls','.json','.xml','.zip','.sql','.ds','.doc','.docx','.dat','.bin','.data','.tmp']

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Create users class
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])

# App verify password
@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

# App Register User
@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return 'Missing Arguments, you might not have typed the username and password.'
    if User.query.filter_by(username=username).first() is not None:
        return 'The user ' + username + ' already exist in database.'
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username},{'status':'User has been successfully created in database.'}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})

# App List Users
@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        return 'User does not exist in database.'
    return jsonify({'username': user.username})

# App Generate Token
@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

# App Resource with authentication
@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

# path variable, using network file share location.
path = "C:/Python/Share/"

# App Route, Root , deny access
@app.route("/")
@auth.login_required
def index():
    return render_template('exception.html')

# App Route /listfiles GET Method, get file name from folder.
@app.route("/listfiles", methods=["GET"])
@auth.login_required
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
@auth.login_required
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
@auth.login_required
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
@auth.login_required
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

# App route /copyfiles POST Method call
@app.route('/copyfiles', methods=['POST'])
@auth.login_required
def copy_files():
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
                        shutil.copyfile(original,target)
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
@auth.login_required
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

# App route /deletefile DELETE Method call
@app.route('/deletefile', methods=['DELETE'])
@auth.login_required
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
if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    #app.run(debug=True)
    app.run()