
from io import BytesIO
from flask import Flask, session, flash, request,send_from_directory, redirect, url_for, render_template, send_file
import urllib.request
import os
import base64

import cv2
from werkzeug.utils import secure_filename
import PIL
from PIL import Image, ImageDraw, ImageOps,UnidentifiedImageError, ImageFont
 
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
    
 
@app.route('/',methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        city = request.form['city']
        email = request.form['email']
        mobile = request.form['mobile']
        return render_template('result.html', name=name, city=city, email=email, mobile=mobile)
    else:
        return render_template('index.html') 


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded'
        file = request.files['file']
        cname = request.form['cname']
        if file.filename == '':
            return 'No file selected'
        if file:
            filename = file.filename
            file.save(os.path.join('uploads', file.filename))
            image = cv2.imread(os.path.join('uploads', file.filename))
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if len(faces) == 0:
                return render_template('result.html', message='No face detected. Please upload another image.')
            else: 
                 return render_template('result.html', cname=cname, filename=filename,file=file)


@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'POST':
        filename = request.form['filename']
        file = request.form['file']
        cname= request.form['cname']
        # print(file,filename)
        
        # Load user image using Pillow library
        user_img = Image.open(f'uploads/{filename}')

        # Load template image using Pillow library
        template_img = Image.open('template.png')

        # Load template image using Pillow library
        template_img = Image.open('template.png')

        font = ImageFont.truetype('arial.ttf', size=30)

        # Create ImageDraw object
        draw = ImageDraw.Draw(template_img)

        # Get size of template image
        width, height = template_img.size

        # Define text to be added below the image
        text = cname

        # Get size of text
        text_width, text_height = draw.textsize(text, font=font)

        # Calculate top-left position of text
        text_x = width // 2 - text_width // 2
        text_y = height - text_height - 30

        # Add text to image
        draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0))

        # Resize user image to fit in template
        user_img = user_img.resize((500, 500))

       # Calculate center position of template image
        template_center_x = template_img.width // 2
        template_center_y = template_img.height // 2

        shrink_percent = 80
        # Calculate new image size based on shrink percentage
        new_width = user_img.width * shrink_percent // 100
        new_height = user_img.height * shrink_percent // 100

         # Resize user image based on new size
        user_img = user_img.resize((new_width, new_height))

        # Create circular mask for user image
        mask = Image.new('L', user_img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, user_img.size[0], user_img.size[1]), fill=255)
        

        # Apply circular mask to user image
        user_img.putalpha(mask)

        # Calculate top-left position of user image
        user_top_left_x = template_center_x - user_img.width // 2
        user_top_left_y = template_center_y - user_img.height // 2

        # Paste user image on template image at center position
        template_img.paste(user_img, (user_top_left_x, user_top_left_y))

        # Save final image
        template_img.save('Greeting_final.png')

        # Download final image
        return send_file('Greeting_final.png', as_attachment=True)
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


    return render_template('result.html')

 
if __name__ == "__main__":
    app.run()