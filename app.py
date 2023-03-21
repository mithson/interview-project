
from io import BytesIO
from flask import Flask, flash, request, redirect, url_for, render_template, send_file
import urllib.request
import os
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageOps
 
app = Flask(__name__)

picFolder = os.path.join('static', 'images')
print(picFolder)
app.config['UPLOAD_FOLDER'] = picFolder 

UPLOAD_FOLDER = 'uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     
 
@app.route('/',methods = ['GET', 'POST'])
def index():
    pic1 = os.path.join(picFolder, 'BG.png')
    if request.method == 'POST':
        name = request.form['name']
        city = request.form['city']
        email = request.form['email']
        mobile = request.form['mobile']
        return render_template('result.html', name=name, city=city, email=email, mobile=mobile, user_image=pic1)
    else:
        return render_template('index.html') 


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get user image from uploaded file
        user_image = request.files['user_image'].read()

        # Load user image using Pillow library
        user_img = Image.open(BytesIO(user_image))

        # Load template image using Pillow library
        template_img = Image.open('template.png')

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

    return render_template('result.html')
 
if __name__ == "__main__":
    app.run()