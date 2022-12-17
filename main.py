from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors
from werkzeug.utils import secure_filename
import os
from werkzeug.security import generate_password_hash, check_password_hash

UPLOAD_FOLDER = 'images'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, f'static/{UPLOAD_FOLDER}')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# Configure MySQL

conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='root',
                       password='root',
                       db='cookzilla',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')


# Define route for login
@app.route('/login')
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')


# Define route for register
@app.route('/register')
def register():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username')
    flash('Successfully logged out', 'success')
    return redirect('/')


# Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()

    query = 'SELECT * FROM Person WHERE username = %s '
    cursor.execute(query, (username,))

    data = cursor.fetchone()

    cursor.close()
    print(data)
    error = None
    if data and check_password_hash(data['password'], password):
        session['username'] = username
        flash('Successfully logged in', 'success')
        return redirect(url_for('home'))
    else:
        flash('Invalid login or username', 'error')
        return render_template('login.html', error=error)


# Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    # grabs information from the forms
    username = request.form.get('username')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    profile = request.form.get('profile')

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM Person WHERE userName = %s'
    cursor.execute(query, (username,))
    # stores the results in a variable
    data = cursor.fetchone()
    print(data)
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if data:
        # If the previous query returns data, then user exists
        flash("This user already exists", 'error')
        return render_template('register.html', error=error)
    else:
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        ins = 'INSERT INTO Person VALUES (%s, %s, %s,%s, %s, %s)'
        cursor.execute(ins, (username, hash_password, first_name, last_name, email, profile))
        conn.commit()
        cursor.close()
        flash('Successfully registered', 'success')
        return render_template('index.html')


@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('hello'))
    user = session['username']
    return render_template('home.html', username=user)


@app.route('/view-recipies')
def view_recipies():
    if 'username' not in session:
        return redirect(url_for('hello'))
    user = session['username']
    cursor = conn.cursor()
    query = 'SELECT recipeID, title FROM Recipe WHERE postedBy = %s ORDER BY recipeID DESC'
    cursor.execute(query, (user,))
    data = cursor.fetchall()
    cursor.close()
    return render_template('view-recipies.html', username=user, recipies=data)


@app.route('/view-allRecipies')
def view_Allrecipies():
    if 'username' not in session:
        return redirect(url_for('hello'))
    user = session['username']
    cursor = conn.cursor()
    query = 'SELECT recipeID, title FROM Recipe ORDER BY recipeID DESC'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('view-recipies.html', username=user, recipies=data)


@app.route('/view-groups', methods = ['GET', 'POST'])
def view_groups():
    if 'username' not in session:
        return redirect(url_for('hello'))
    user = session['username']

    cursor = conn.cursor()
    query = 'SELECT * FROM `Group`'
    cursor.execute(query,)
    data = cursor.fetchall()
    cursor.close()

    return render_template('view-groups.html', groups=data)

@app.route('/join-group', methods=['GET','POST'])
def joinGroup():
    
    if 'username' not in session:
        return redirect(url_for('hello'))
    user = session['username']
    cursor = conn.cursor()
    gName = request.form['gName']
    gCreator = request.form['gCreator']
    
    query = 'SELECT gName FROM groupmembership WHERE memberName = %s and gName = %s and gCreator = %s'
    cursor.execute(query,(user, gName, gCreator))
    data = cursor.fetchall()
    if data:
        flash(f'Already a member of this group')    
    else:
        query = "INSERT into GroupMembership VALUES(%s,%s,%s)"
        cursor.execute(query,(user, gName, gCreator))
        conn.commit()
        cursor.close()
        flash(f'successfully Joined this group :{gName}')
            
    
    return redirect('/view-groups')


    
@app.route('/rsvpEvent', methods=['GET','POST'])
def rsvpEvent():
    
    if 'username' not in session:
        return redirect(url_for('hello'))
    user = session['username']
    cursor = conn.cursor()
    eID = request.form['eID']
    eName = request.form['eName']
    
    query = 'SELECT eID FROM rsvp WHERE userName = %s and eID = %s'
    cursor.execute(query,(user, eID))
    data = cursor.fetchall()
    if data:
        flash(f'Already did RSVP to this event')    
    else:
        query = "INSERT into rsvp VALUES(%s,%s,%s)"
        cursor.execute(query,(user,eID,'y'))
        conn.commit()
        cursor.close()
        flash(f'successfully completed Rsvp to this group :{eName}')
            
    
    return redirect('/view-createdEvents')


@app.route('/view-createdEvents')
def view_CreatedEvents():
    if 'username' not in session:
        return redirect(url_for('hello'))
    user = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM event'
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)
    cursor.close()

    return render_template('view-createdEvents.html', username=user, events=data)


@app.route('/view-EventPictures', methods=['GET', 'POST'])
def groupPics():
    
    if 'username' not in session:
        return redirect(url_for('hello'))
    user = session['username']
    
    eID = request.form['eID']
    
    query = 'SELECT * FROM EventPicture WHERE eID = %s'
    cursor=conn.cursor()
    cursor.execute(query, eID)
    
    data = cursor.fetchall()
    
    return render_template('event-Pictures.html', eventPictues=data)


@app.route('/view-events')
def view_events():
    if 'username' not in session:
        return redirect(url_for('hello'))
    user = session['username']
    cursor = conn.cursor()
    query = 'SELECT eDate, eName, eDesc FROM event e join rsvp r on e.eID = r.eID WHERE r.username = % s '
    cursor.execute(query, (user,))
    data = cursor.fetchall()
    
    print(data)
    cursor.close()

    return render_template('view-events.html', username=user, events=data)


@app.route('/view-rsvp')
def view_rsvp():
    if 'username' not in session:
        return redirect(url_for('hello'))
    user = session['username']
    cursor = conn.cursor()
    query = 'SELECT eName, eID FROM event natural join RSVP WHERE userName = % s '
    cursor.execute(query, (user,))
    data = cursor.fetchall()
    cursor.close()
    return render_template('view-rsvp.html', username=user, rsvps=data)


@app.route('/create-event', methods=["GET", "POST"])
def create_event():
    if 'username' not in session:
        return redirect(url_for('hello'))
    username = session['username']
    if request.method == "POST":
        group_name = request.form.get('group_name')
        event_name = request.form.get('event_name')
        event_description = request.form.get('event_description', None)
        event_date = request.form.get('event_date')

        cursor = conn.cursor()
        query = 'SELECT * FROM `Group` WHERE gName = %s And gCreator = %s'
        cursor.execute(query, (group_name, username,))
        group_data = cursor.fetchone()

        print(group_data)
        if group_data:
            query = 'INSERT INTO Event (eName,eDesc,eDate,gName,gCreator) VALUES(%s,%s,%s,%s,%s)'
            cursor.execute(query, (event_name, event_description,
                           event_date, group_name, username))
            conn.commit()

            event_picture_lst = request.files.getlist("file[]")

            for file in event_picture_lst:
                print(file)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    print(filename)
                    file.save(os.path.join(
                        app.config['UPLOAD_FOLDER'], filename))

                    query = 'INSERT INTO eventPicture (pictureURL, eID) VALUES(%s, %s)'
                    eID = cursor.lastrowid
                    cursor.execute(query, (filename, eID))
                    conn.commit()
                    
            cursor.close()
            flash(f'Successfully added Event')
        else:
            flash(f'Only group creaters of this group can create the event: {group_name} ')
        return redirect('/home')
    return render_template('create-event.html')



@app.route('/create-recipie', methods=['GET', 'POST'])
def create_recipie():
    if 'username' not in session:
        return redirect(url_for('hello'))
    username = session['username']
    if request.method == "POST":
        recipie_title = request.form.get('title')
        number_of_servings = request.form.get('num_of_serve')
        print(recipie_title, number_of_servings)

        if recipie_title and number_of_servings:
            cursor = conn.cursor()
            query = 'INSERT INTO Recipe (title, numServings,postedBy) VALUES(%s, %s, %s)'
            cursor.execute(query, (recipie_title, number_of_servings, username))
            conn.commit()
            recipie_id = cursor.lastrowid

            step_num_lst = request.form.getlist('step_num')
            step_description_lst = request.form.getlist('step_description')

            print(step_num_lst, step_description_lst)
            for step_num, step_description in zip(step_num_lst, step_description_lst):
                print(step_num, step_description)
                query = 'INSERT INTO Step (stepNo,sDesc, recipeID) VALUES(%s, %s, %s)'
                cursor.execute(query, (step_num, step_description, recipie_id))
                conn.commit()

            ingredient_name_lst = request.form.getlist('ingredient_name')
            ingredient_purchase_link_lst = request.form.getlist('ingredient_purchase_link')
            unit_name_lst = request.form.getlist('unit_name')
            unit_amount_lst = request.form.getlist('unit_amount')

            for ingredient_name, ingredient_purchase_link, unit_name, unit_amount in zip(ingredient_name_lst,
                                                                                         ingredient_purchase_link_lst,
                                                                                         unit_name_lst,
                                                                                         unit_amount_lst):
                print(ingredient_name, ingredient_purchase_link, unit_name, unit_amount)

                query = 'SELECT * FROM Unit WHERE unitName = %s '
                cursor.execute(query, unit_name)
                ingredient_data = cursor.fetchone()

                if not ingredient_data:
                    query = 'INSERT INTO Ingredient (iName, purchaseLink) VALUES(%s, %s)'
                    cursor.execute(query, (ingredient_name, ingredient_purchase_link))
                    conn.commit()

                query = 'SELECT * FROM Unit WHERE unitName = %s '
                cursor.execute(query, unit_name)
                unit_data = cursor.fetchone()

                if unit_data is None:
                    query = 'INSERT INTO Unit (unitName) VALUES(%s)'
                    cursor.execute(query, (unit_name,))
                    conn.commit()

                query = 'INSERT INTO RecipeIngredient (recipeID, iName,unitName,amount) VALUES(%s, %s, %s, %s)'
                cursor.execute(query, (recipie_id, ingredient_name, unit_name, unit_amount))
                conn.commit()

            tag_text_lst = request.form.getlist('tag_text')

            for tag_text in tag_text_lst:
                print(tag_text)
                query = 'INSERT INTO RecipeTag (tagText, recipeID) VALUES(%s, %s)'
                cursor.execute(query, (tag_text, recipie_id))
                conn.commit()

            recipie_picture_lst = request.files.getlist("file[]")

            for file in recipie_picture_lst:
                print(file)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    print(filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    query = 'INSERT INTO RecipePicture (pictureURL, recipeID) VALUES(%s, %s)'
                    cursor.execute(query, (filename, recipie_id))
                    conn.commit()

            cursor.close()
            flash(f'successfully created recipie which id is :{recipie_id}')
            return redirect(url_for('home'))
    return render_template('create-recipie.html')


@app.route('/create-step', methods=['GET', 'POST'])
def create_recipie_step():
    if 'username' not in session:
        return redirect(url_for('hello'))
    username = session['username']
    if request.method == "POST":
        recipie_id = request.form.get('recipie_id')
        step_num = request.form.get('step_num')
        step_description = request.form.get('step_description')

        cursor = conn.cursor()

        query = 'SELECT recipeID, title FROM Recipe WHERE recipeID = %s AND postedBy = %s '
        cursor.execute(query, (recipie_id, username,))
        data = cursor.fetchone()

        if data:
            query = 'INSERT INTO Step (stepNo,sDesc, recipeID) VALUES(%s, %s, %s)'
            cursor.execute(query, (step_num, step_description, recipie_id))
            conn.commit()
            cursor.close()
            flash(f'successfully Added step to this recipie :{recipie_id}')
        else:
            flash(f'recipie with this id is not available:{recipie_id}')
        return redirect(url_for('home'))
    return render_template('create-step.html')


@app.route('/create-tag', methods=['GET', 'POST'])
def create_recipie_tag():
    if 'username' not in session:
        return redirect(url_for('hello'))
    username = session['username']
    if request.method == "POST":
        recipie_id = request.form.get('recipie_id')
        tag_text = request.form.get('tag_text')
        cursor = conn.cursor()

        query = 'SELECT recipeID, title FROM Recipe WHERE recipeID = %s AND postedBy = %s '
        cursor.execute(query, (recipie_id, username,))
        data = cursor.fetchone()

        if data:
            query = 'INSERT INTO RecipeTag (tagText, recipeID) VALUES(%s, %s)'
            cursor.execute(query, (tag_text, recipie_id))
            conn.commit()
            flash(f'successfully Added tag to this recipie :{recipie_id}')
        else:
            flash(f'recipie with this id is not available:{recipie_id}')

        cursor.close()

        return redirect(url_for('home'))
    return render_template('create-tag.html')


@app.route('/create-ingredient', methods=['GET', 'POST'])
def create_recipie_ingredient():
    if 'username' not in session:
        return redirect(url_for('hello'))
    username = session['username']
    if request.method == "POST":
        recipie_id = request.form.get('recipie_id')
        ingredient_name = request.form.get('ingredient_name')
        ingredient_purchase_link = request.form.get('ingredient_purchase_link', None)
        unit_name = request.form.get('unit_name')
        unit_amount = request.form.get('unit_amount')

        cursor = conn.cursor()

        query = 'SELECT recipeID, title FROM Recipe WHERE recipeID = %s AND postedBy = %s '
        cursor.execute(query, (recipie_id, username,))
        data = cursor.fetchone()

        if data:

            query = 'SELECT * FROM ingredient WHERE iName = %s '
            cursor.execute(query, ingredient_name)
            ingredient_data = cursor.fetchone()

            if not ingredient_data:
                query = 'INSERT INTO ingredient (iName, purchaseLink) VALUES(%s, %s)'
                cursor.execute(query, (ingredient_name, ingredient_purchase_link))
                conn.commit()

            query = 'SELECT * FROM Unit WHERE unitName = %s '
            cursor.execute(query, unit_name)
            unit_data = cursor.fetchone()

            if unit_data is None:
                query = 'INSERT INTO unit (unitName) VALUES(%s)'
                cursor.execute(query, (unit_name,))
                conn.commit()

            query = 'INSERT INTO recipeIngredient (recipeID, iName, unitName,amount) VALUES(%s, %s, %s, %s)'
            cursor.execute(query, (recipie_id, ingredient_name, unit_name, unit_amount))
            conn.commit()
            flash(f'successfully Added Ingredient to this recipie :{recipie_id}')
        else:
            flash(f'recipie with this id is not available:{recipie_id}')

        cursor.close()

        return redirect(url_for('home'))
    return render_template('create-ingredient.html')


@app.route('/upload-recipie-picture', methods=['GET', 'POST'])
def upload_recipie_picture():
    if 'username' not in session:
        return redirect(url_for('hello'))
    username = session['username']
    if request.method == "POST":
        recipie_id = request.form.get('recipie_id')
        if 'recipie_picture' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['recipie_picture']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)

        cursor = conn.cursor()

        query = 'SELECT recipeID, title FROM Recipe WHERE recipeID = %s AND postedBy = %s '
        cursor.execute(query, (recipie_id, username,))
        data = cursor.fetchone()

        if data:
            query = 'INSERT INTO RecipePicture (pictureURL, recipeID) VALUES(%s, %s)'
            cursor.execute(query, (filename, recipie_id))
            conn.commit()
            flash(f'successfully Added Recipie picture to this recipie :{recipie_id}')
        else:
            flash(f'recipie with this id is not available:{recipie_id}')
        cursor.close()
        return redirect(url_for('home'))
    return render_template('upload-recipie-picture.html')


@app.route('/upload-event-picture', methods=['GET', 'POST'])
def upload_event_picture():
    if 'username' not in session:
        return redirect(url_for('hello'))
    username = session['username']
    if request.method == "POST":
        eID = request.form.get('eID')
        if 'event_picture' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['event_picture']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)

        cursor = conn.cursor()

        query = 'SELECT eID FROM event WHERE eID = %s '
        cursor.execute(query, (eID))
        data = cursor.fetchone()

        if data:
            query = 'INSERT INTO eventPicture (pictureURL, eID) VALUES(%s, %s)'
            cursor.execute(query, (filename, eID))
            conn.commit()
            flash(f'successfully Added Event picture for this event: {eID}')
        else:
            flash(f'Event for this id is not available:{eID}')
        cursor.close()
        return redirect(url_for('home'))
    return render_template('upload-event-picture.html')


@app.route('/recipie-detail/<id>')
def recipie_details(id):
    print(id)
    cursor = conn.cursor()

    query = 'SELECT * FROM Recipe WHERE recipeID = %s'
    cursor.execute(query, (id,))
    # stores the results in a variable
    recipie = cursor.fetchone()
    print(recipie)

    query = 'SELECT * FROM RecipeTag WHERE recipeID = %s'
    cursor.execute(query, (id,))
    recipie_tag = cursor.fetchall()
    print(recipie_tag)

    query = 'SELECT * FROM RecipePicture WHERE recipeID = %s'
    cursor.execute(query, (id,))
    recipie_picture = cursor.fetchall()
    print(recipie_picture)

    query = 'SELECT * FROM Step WHERE recipeID = %s'
    cursor.execute(query, (id,))
    step = cursor.fetchall()
    print(step)

    query = 'SELECT * FROM RecipeIngredient WHERE recipeID = %s'
    cursor.execute(query, (id,))
    recipie_ingredient = cursor.fetchall()
    print(recipie_ingredient)

    # Review section
    query = 'SELECT * FROM Review WHERE recipeID = %s'
    cursor.execute(query, (id,))
    reviews = cursor.fetchall()
    print(reviews)

    query = 'SELECT * FROM ReviewPicture WHERE recipeID = %s'
    cursor.execute(query, (id,))
    review_pictures = cursor.fetchall()
    print(review_pictures)

    cursor.close()
    return render_template('recipie-detail.html',
                           recipie=recipie,
                           recipie_picture=recipie_picture,
                           recipie_ingredient=recipie_ingredient,
                           recipie_tag=recipie_tag,
                           step=step,
                           reviews=reviews,
                           review_pictures=review_pictures)


@app.route('/rsvp-event-detail/<id>')
def rsvp_event_detail_view(id):
    cursor = conn.cursor()

    query = 'SELECT * FROM RSVP WHERE eID = %s'
    cursor.execute(query, (id,))

    rsvp_event = cursor.fetchone()

    query = 'SELECT * FROM Event WHERE eID = %s'
    cursor.execute(query, (id,))

    event = cursor.fetchone()
    print(event)
    return render_template('rsvp-event-detail.html', event=event, rsvp_event=rsvp_event)


@app.route('/recipie-review', methods=['POST'])
def recipie_review():
    if 'username' not in session:
        return redirect(url_for('hello'))
    username = session['username']
    recipie_id = request.form.get('recipie_id')
    print(recipie_id)
    review_title = request.form.get('revTitle')
    review_description = request.form.get('revDesc')
    review_stars = request.form.get('stars')
    print(review_title, review_description, review_stars)
    if 'review_picture' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['review_picture']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
        return redirect(request.url)

    if filename and review_title and review_description and review_stars:
        try:
            cursor = conn.cursor()

            query = 'INSERT INTO Review (revTitle, revDesc,stars,userName,recipeID) VALUES(%s, %s, %s,%s, %s)'
            cursor.execute(query, (review_title, review_description, review_stars, username, recipie_id))
            conn.commit()

            query = 'INSERT INTO ReviewPicture (pictureURL, userName,recipeID) VALUES(%s, %s, %s)'
            cursor.execute(query, (filename, username, recipie_id))
            conn.commit()

            cursor.close()
            flash(f'successfully Added Recipie picture to this recipie :{recipie_id}')
        except Exception:
            flash(f'You already reviewed this recipie')
    else:
        flash(f'all details is required to post a review')
    return redirect(url_for('home'))


@app.route('/search', methods=["GET", "POST"])
def show_recipies():
    term = request.args['search']
    cursor = conn.cursor()
    recipies= []

    print(term)
    if(term.find('and') != -1):
            search = term.split('and')
            query = """select * from recipe r left join recipetag rt on r.recipeID = rt.recipeID 
                    left join review rw on r.recipeID = rw.recipeID where rt.tagText = %s
                        and rw.stars = %s"""
            cursor.execute(query, (search[0].strip(),int(search[1].strip())))
            reviews = cursor.fetchall()
            print(reviews)
            lst_id = []
            for review in reviews:
                lst_id.append(review['recipeID'])
            for i in lst_id:
                query = 'SELECT recipeID, title FROM Recipe WHERE recipeID = %s ORDER BY recipeID DESC'
                cursor.execute(query, (i,))
                recipie = cursor.fetchone()
                recipies.append(recipie)
                
    elif(term.find('or') != -1):
            search = term.split('or')
            query = """select * from recipe r left join recipetag rt on r.recipeID = rt.recipeID 
                    left join review rw on r.recipeID = rw.recipeID where rt.tagText = %s
                        or rw.stars = %s"""
            cursor.execute(query, (search[0].strip(),int(search[1].strip())))
            reviews = cursor.fetchall()
            print(reviews)
            lst_id = []
            for review in reviews:
                lst_id.append(review['recipeID'])
            for i in lst_id:
                query = 'SELECT recipeID, title FROM Recipe WHERE recipeID = %s ORDER BY recipeID DESC'
                cursor.execute(query, (i,))
                recipie = cursor.fetchone()
                recipies.append(recipie)
                
    elif term.isnumeric():
            query = 'SELECT * FROM Review WHERE stars = %s'
            cursor.execute(query, (int(term)))
            reviews = cursor.fetchall()
            print(reviews)
            lst_id = []
            for review in reviews:
                lst_id.append(review['recipeID'])
            for i in lst_id:
                query = 'SELECT recipeID, title FROM Recipe WHERE recipeID = %s ORDER BY recipeID DESC'
                cursor.execute(query, (i,))
                recipie = cursor.fetchone()
                recipies.append(recipie)
    else:
            query = 'SELECT * FROM RecipeTag WHERE tagText = %s '
            cursor.execute(query, term)
            data = cursor.fetchall()
            print(data)
            lst_id = []
            for i in data:
                lst_id.append(i['recipeID'])
            for i in lst_id:
                query = 'SELECT recipeID, title FROM Recipe WHERE recipeID = %s ORDER BY recipeID DESC'
                cursor.execute(query, (i,))
                recipie = cursor.fetchone()
                recipies.append(recipie)

    cursor.close()
    return render_template('result.html', query=term, recipies=recipies)

@app.route('/search-title', methods=["GET", "POST"])
def show_recipies_id():
    search = request.args['search']
    cursor = conn.cursor()
    query = 'SELECT recipeID, title FROM Recipe WHERE title like %s ORDER BY title DESC'
    cursor.execute(query, ("%" + search + "%"))
    recipies = cursor.fetchall()
    print(recipies)
    cursor.close()
    return render_template('result.html', query=search, recipies=recipies)

@app.route('/create-group', methods=["GET", "POST"])
def create_group():
    if 'username' not in session:
        return redirect(url_for('hello'))
    username = session['username']
    if request.method == "POST":
        group_name = request.form.get('group_name')
        group_description = request.form.get('group_description', None)

        cursor = conn.cursor()
        query = 'SELECT * FROM `Group` WHERE gName = %s '
        cursor.execute(query, group_name)
        group_data = cursor.fetchone()

        print(group_data)
        if group_data is None:
            query = 'INSERT INTO `Group` (gName,gDesc,gCreator) VALUES(%s,%s,%s)'
            cursor.execute(query, (group_name, group_description, username))
            conn.commit()
            flash('Successfully added Group')
        else:
            flash("Group with that name is already taken")

        cursor.close()
        return redirect('/home')
    return render_template('create-group.html')



@app.route('/create-rsvp', methods=["GET", "POST"])
def create_rsvp():
    if 'username' not in session:
        return redirect(url_for('hello'))
    username = session['username']
    if request.method == "POST":
        event_id = request.form.get('event_id')
        response = request.form.get('response')

        cursor = conn.cursor()
        query = 'SELECT * FROM Event WHERE eID = %s And gCreator = %s'
        cursor.execute(query, (event_id, username,))
        event_data = cursor.fetchone()

        print(event_data)
        if event_data:
            query = 'INSERT INTO RSVP (userName,eID,response) VALUES(%s,%s,%s)'
            cursor.execute(query, (username, event_id, response))
            conn.commit()
            flash('Successfully added Rsvp Event')
        else:
            flash(f'Event with this id: {event_id} is not available')

        cursor.close()

        return redirect('/home')
    return render_template('create-rsvp.html')


if __name__ == "__main__":
    app.run(debug=True)
