from flask import Flask, render_template, flash, url_for, session, redirect
import os
import sys
from flask import request
from random import randint
from werkzeug.utils import secure_filename
from flask.ext.session import Session
import glob
from zipfile import ZipFile
from PIL import Image
import numpy as np

from wordcloud import WordCloud, STOPWORDS

UPLOAD_FOLDER = os.path.join('static', 'image')
ALLOWED_EXTENSIONS = set(['zip'])
OUTPUT_IMAGE_NAME = 'output.png'
BASE_IMAGE_NAME = 's14.png' 

app = Flask(__name__)
sess = Session()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_IMAGE_NAME'] = OUTPUT_IMAGE_NAME
app.config['BASE_IMAGE_NAME'] = BASE_IMAGE_NAME

@app.route('/', methods=['GET', 'POST'])
def home():
    
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
def create_code_cloud(content):

    # read the mask image
    image_base = np.array(Image.open(os.path.join(app.config['UPLOAD_FOLDER'], app.config['BASE_IMAGE_NAME'])))
    
    stopwords = set(STOPWORDS)
    
    wc = WordCloud(background_color="white", max_words=2500, mask=image_base,
                   stopwords=stopwords, contour_width=3, contour_color='steelblue')
    
    # generate word cloud
    wc.generate(content)
    
    # store to file
    #wc.to_file("output.png")
    #wc.to_file("output.png")
    output_image_path = os.path.join(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_IMAGE_NAME'])
    wc.to_file(output_image_path)
    
    print('Converted')
    
    return output_image_path 
            

@app.route('/upload_file', methods=['POST'])
def upload_file():
    
    # check if the post request has the file part
    if 'file' not in request.files:        
        result = {
            'result' : 0,    
            'error' : 'file not available',
        }
        return render_template('result.html', result=result)
    
    file = request.files['file']
    
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':        
        result = {
            'result' : 0,    
            'error' : 'file is empty',
        }
        return render_template('result.html', result=result)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)
        
        '''
        archive = ZipFile(filepath, 'r')
        files = archive.namelist()
        
        first_file = ''
        
        for x in files:
            print(x)
            if(x.endswith('.py')):
                print('py file : '+str(x))
                first_file = x
                
        print(first_file+' selected')
        #create_code_cloud(os.path.join(app.config['UPLOAD_FOLDER'], first_file))
        '''
        
        content = ''
        
        with ZipFile(filepath) as z:
            for filename in z.namelist():
                if not os.path.isdir(filename):
                    
                    if not (filename.endswith('.py')):
                        continue
                        
                    print('py file : '+str(filename))
                    
                    # read the file                
                    with z.open(filename) as f:
                        for line in f:
                            #print(line)
                            content = content + str(line.decode("utf-8") )
            
        # read only python file
        
        # create cloud
        img_path = create_code_cloud(content)
        
        result = {
            'result' : 1,
            'img_path' : img_path,
            'error' : '',
        }
        return render_template('result.html', result=result)
    
    #return content
    return render_template('result.html', user=user)

if __name__ == '__main__':
    host = os.environ.get('IP', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    sess.init_app(app)
    
    app.run(host= host, port = port, use_reloader = False)
    
    
'''
Sources:
    http://www.compjour.org/lessons/flask-single-page/multiple-dynamic-routes-in-flask/
    
    https://www.learnpython.org/en/String_Formatting
    
    https://stackoverflow.com/questions/25888396/how-to-get-latitude-longitude-with-python
    
    https://github.com/googlemaps/google-maps-services-python
    
    AIzaSyCRhRz_mw_5wIGgF-I6PUy3js6dcY6zQ6Q
    
    Get Current Location:
    https://stackoverflow.com/questions/44218836/python-flask-googlemaps-get-users-current-location-latitude-and-longitude
    
    File Upload:
        http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
        
    Read a zip file:
        https://stackoverflow.com/questions/19371860/python-open-file-from-zip-without-temporary-extracting-it
        
    https://stackoverflow.com/questions/22646623/how-to-read-text-files-in-a-zipped-folder-in-python
    
    https://stackoverflow.com/questions/46588075/read-all-files-in-zip-archive-in-python
    
    byte to String:
        https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
    
    Display image:
        https://stackoverflow.com/questions/46785507/python-flask-display-image-on-a-html-page
        
    https://github.com/gitpython-developers/GitPython
    
    Image issue:
        https://stackoverflow.com/questions/34901523/file-url-not-allowed-to-load-local-resource-in-the-internet-browser
        https://stackoverflow.com/questions/22026984/trying-to-disable-chrome-same-origin-policy/22027002#22027002
'''