## Python File Management REST API
This Python flask api has the function of acting as a smb file share hub, letting computers to operate through HTTP in the file share where the api is hosted.<br>
For example, copying files, uploading files, moving files, renaming files and more.

## Usage
1) install all python libraries mentioned in the requirements.txt
2) Replace the path variable value with the folder path you want to share.<br>
This can be found at row 106 on file main.py
```
Locate the variable "path" and replace its value for ex:

# path variable, using network file share location.
path = "C:/Python/Share/"

```
3) host the api and test it.

## Credits
Matheus Pavanetti - 2021  
(matheuspavanetti@gmail.com)

## Contributors
New Contributors are always welcome !

## Notes
As this is a beta version, bugs may be found, if you find some, please report immediatly !
