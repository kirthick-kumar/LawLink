from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from typing import List
from functools import wraps
from datetime import date
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random


admins = ['1']
app = Flask(__name__, static_folder=r'D:\Studies\Pycharm\Projects\Chat Test\static')
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
Bootstrap5(app)
socketio = SocketIO(app)
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lawlink.db"
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.init_app(app)
smtp_email = 'lawlinkotp@gmail.com'
smtp_password = 'hkvcjhlajwemyive'
to_email = 'lawlinkotp@gmail.com'
otp = 0
chats = ''
names = []
msgs = []
rating_dict = {
    5: '🌕🌕🌕🌕🌕',
  4.7: '🌕🌕🌕🌕🌖',
  4.5: '🌕🌕🌕🌕🌗',
  4.2: '🌕🌕🌕🌕🌘',
    4: '🌕🌕🌕🌕🌑',
  3.7: '🌕🌕🌕🌖🌑',
  3.5: '🌕🌕🌕🌗🌑',
  3.2: '🌕🌕🌕🌘🌑',
    3: '🌕🌕🌕🌑🌑',
  2.7: '🌕🌕🌖🌑🌑',
  2.5: '🌕🌕🌗🌑🌑',
  2.2: '🌕🌕🌘🌑🌑',
    2: '🌕🌕🌑🌑🌑',
  1.7: '🌕🌖🌑🌑🌑',
  1.5: '🌕🌗🌑🌑🌑',
  1.2: '🌕🌘🌑🌑🌑',
    1: '🌕🌑🌑🌑🌑',
}


class User(db.Model, UserMixin):
    __table_name__ = 'user'
    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    # Relationship
    lawyer: db.Mapped["Lawyer"] = db.relationship(back_populates="user")
    rating_user: db.Mapped[List["Rating"]] = db.relationship(back_populates="rating_author")

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Lawyer(db.Model, UserMixin):
    __table_name__ = 'lawyer'
    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    pic_url = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.String(200), nullable=False)
    education = db.Column(db.String(20), nullable=False)
    bar_council_id = db.Column(db.Integer, nullable=False, unique=True)
    location = db.Column(db.String(200), nullable=False)
    expertise = db.Column(db.String(200), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    ongoing = db.Column(db.Integer, nullable=False)
    won = db.Column(db.Integer, nullable=False)
    lost = db.Column(db.Integer, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    phone = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(200), nullable=False)
    fee = db.Column(db.Integer, nullable=False)
    id_url = db.Column(db.String(200), nullable=False)
    verified_sum = db.Column(db.Integer, default=0)
    verified_count = db.Column(db.Integer, default=0)
    # Relationship
    user: db.Mapped["User"] = db.relationship(back_populates="lawyer")
    user_id: db.Mapped[int] = db.mapped_column(db.ForeignKey("user.id"))
    lawyer_rating: db.Mapped[List["Rating"]] = db.relationship(back_populates="lawyer")
    lawyer_contact: db.Mapped[List["Contact"]] = db.relationship(back_populates="lawyer")

    # name, pic_url, bio, education, bar_council_id, location, expertise, experience, ongoing, won, lost
    # user, user_id, lawyer_rating, lawyer_contact


class Rating(db.Model, UserMixin):
    __table_name__ = 'rating'
    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    review = db.Column(db.String(200), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    rating_date = db.Column(db.String(20), nullable=False)
    # Put thin in lawyer table

    # Relationship
    rating_author: db.Mapped["User"] = db.relationship(back_populates="rating_user")
    author_id: db.Mapped[int] = db.mapped_column(db.ForeignKey("user.id"))
    lawyer: db.Mapped["Lawyer"] = db.relationship(back_populates="lawyer_rating")
    lawyer_id: db.Mapped[int] = db.mapped_column(db.ForeignKey("lawyer.id"))


class Contact(db.Model, UserMixin):
    __table_name__ = 'rating'
    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    socials = db.Column(db.String(200), nullable=False)
    usernames = db.Column(db.String(200), default=False)
    # Relationship
    lawyer: db.Mapped["Lawyer"] = db.relationship(back_populates="lawyer_contact")
    lawyer_id: db.Mapped[int] = db.mapped_column(db.ForeignKey("lawyer.id"))


with app.app_context():
    db.create_all()


def delete_profile(lawyer_id):
    lawyer = db.session.execute(db.select(Lawyer).where(Lawyer.id == lawyer_id)).scalar()
    ratings = db.session.execute(db.select(Rating).where(Rating.lawyer_id == lawyer_id)).scalars()
    contacts = db.session.execute(db.select(Contact).where(Contact.lawyer_id == lawyer_id)).scalars()
    for rating in ratings:
        db.session.delete(rating)
    for contact in contacts:
        db.session.delete(contact)
    db.session.delete(lawyer)


def retrieve_chat():
    """Retrieves messages from chat history text file"""
    global chats, names, msgs
    chats = ''
    names = []
    msgs = []
    # Retrieve chat history without last line '/n'
    with open("Chat History/chat.txt", mode='r') as file:
        chats += file.read()
    chats = chats[:-1]
    if chats:
        chat_list = chats.split('\n')
        for chat in chat_list:
            n = chat.index(':') + 1
            # Characters before : are names .ie., from 0 to n
            names.append(chat[:n])
            # Characters after : are msgs .ie., from n to end
            msgs.append(chat[n:])


def admin_only(function):
    """Decorator function to check if the current user is an admin"""
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if current_user.get_id() in admins:
            return function(*args, **kwargs)
        else:
            flash("Login in as an admin to access that page", "error")
            return redirect(url_for('login'))

    return wrapper_function


@app.route('/')
def home():
    return render_template('index.html')


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).where(User.id == user_id)).scalar()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        log_user = db.session.execute(db.Select(User).where(User.email == email)).scalar()
        if log_user:
            # To check if email and password are both correct
            if log_user.password == password:
                login_user(log_user)
                if log_user.lawyer:
                    return redirect(url_for('profile', lawyer_id=log_user.lawyer.id))
                else:
                    return redirect(url_for('search'))
            else:
                flash('Invalid Password', 'error')
        else:
            flash('Invalid Email', 'error')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global otp
    if request.method == 'POST':
        name = request.form['name']
        user_email = request.form['email']
        user_password = request.form['password']

        otp = random.randint(100000, 999999)
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = user_email
        msg['Subject'] = f'LawLink OTP'
        # Email body
        body = f'Email: {user_email} has been used to register to LawLink Website, please enter the otp mentioned below into the signup form to verify the email\nOTP: {otp}'
        # Attach body to the message
        msg.attach(MIMEText(body, 'plain'))
        # Establish a connection to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # Login to Gmail
        server.login(smtp_email, smtp_password)
        # Send email
        server.sendmail(smtp_email, user_email, msg.as_string())
        # Close the SMTP server connection
        server.quit()
        return render_template('otp.html', name=name, user_email=user_email, user_password=user_password)
    return render_template('signup.html')


@app.route('/signup/otp', methods=['GET', 'POST'])
def send_otp():
    global otp
    name = ''
    user_email = ''
    user_password = ''
    if request.method == 'POST':
        name = request.form['name']
        user_email = request.form['email']
        user_password = request.form['password']
        print(name, user_email, user_password, 'dfa')
        try:
            # User is a lawyer, value = 'on'
            lawyer = request.form['lawyer']
        except:
            # except when 'lawyer' does not exist error
            lawyer = 'off'
        if int(request.form['otp']) == otp:
            # Save to user database
            try:
                user = User(username=name,
                            email=user_email,
                            password=user_password)
                db.session.add(user)
                db.session.commit()
                login_user(user)
            except:
                flash('Email already registered to LawLink', 'error')
                return render_template('login.html')
        else:
            flash('Invalid OTP', 'error')
            return render_template('otp.html', name=name, user_email=user_email, user_password=user_password)

        if lawyer == 'on':
            # Redirect user to create a profile
            return redirect(url_for('profile_edit'))
        else:
            return redirect(url_for('search'))

    return render_template('otp.html', name=name, user_email=user_email, user_password=user_password)


@app.route('/editprofile/', methods=['GET', 'POST'])
@login_required
def profile_edit():
    lawyer_id = current_user.get_id()
    lawyer = db.session.execute(db.Select(Lawyer).where(Lawyer.user_id == lawyer_id)).scalar()
    if request.method == 'POST':
        pic = request.files['lawyer_pic']
        pic.filename = str(lawyer_id)+".png"
        pic_url = os.path.join('static/lawyer_pics/', pic.filename)
        pic.save(pic_url)

        id_pic = request.files['id_pic']
        id_pic.filename = str(lawyer_id)+".png"
        id_pic_url = os.path.join('static/id_pics/', id_pic.filename)
        id_pic.save(id_pic_url)

        pic_url = os.path.join('lawyer_pics/', pic.filename)
        id_url = os.path.join('id_pics/', id_pic.filename)
        name = request.form['name']
        bio = request.form['bio']
        education = request.form['education']
        bar_council_id = request.form['id']
        expertise = request.form['expertise']
        location = request.form['location']
        experience = request.form['experience']
        ongoing = request.form['ongoing']
        won = request.form['won']
        lost = request.form['lost']
        email = request.form['email']
        phone = request.form['phone']
        fee = request.form['fee']
        contacts = request.form['contact'][:-1]
        contact_list = contacts.split('|')
        if lawyer:
            # Editing profile since lawyer profile already exists
            lawyer.name = name
            lawyer.pic_url = pic_url
            lawyer.id_url = id_url
            lawyer.bio = bio
            lawyer.education = education
            lawyer.bar_council_id = bar_council_id
            lawyer.location = location
            lawyer.expertise = expertise
            lawyer.experience = experience
            lawyer.ongoing = ongoing
            lawyer.won = won
            lawyer.lost = lost
            lawyer.email = email
            lawyer.phone = phone
            contact_infos = db.session.execute(db.Select(Contact).where(Contact.lawyer_id == lawyer.id)).scalars()
            for contact_info in contact_infos:
                db.session.delete(contact_info)
            for contact in contact_list:
                n = contact.index(':') + 1
                # Characters before : are social media names .ie., from 0 to n
                # Characters after : are usernames .ie., from n to end
                new_contact = Contact(
                    socials=contact[:n],
                    usernames=contact[n:],
                    lawyer=lawyer
                )
                db.session.add(new_contact)
        else:
            # Create profile and save to lawyer database
            try:
                lawyer = Lawyer(name=name,
                                pic_url=pic_url,
                                id_url=id_url,
                                bio=bio,
                                education=education,
                                bar_council_id=bar_council_id,
                                location=location,
                                expertise=expertise,
                                experience=experience,
                                ongoing=ongoing,
                                won=won,
                                lost=lost,
                                phone=request.form['phone'],
                                email=request.form['email'],
                                fee=fee,
                                user=current_user)
                db.session.add(lawyer)
                db.session.commit()
            except:
                flash('Bar Council ID already registered to LawLink', 'error')
                return redirect(url_for('profile_edit'))
            # Adding Contact information to Contact Database
            contacts = request.form['contact'][:-1]
            contact_list = contacts.split('|')
            for contact in contact_list:
                n = contact.index(':') + 1
                # Characters before : are social media names .ie., from 0 to n
                # Characters after : are usernames .ie., from n to end
                print(contact[:n], contact[n:])
                new_contact = Contact(
                    socials=contact[:n],
                    usernames=contact[n:],
                    lawyer=lawyer
                )
                db.session.add(new_contact)
        db.session.commit()
        return redirect(url_for('profile', lawyer_id=lawyer.id))
    return render_template('profile_edit.html', lawyer=lawyer)


@app.route('/profile/<lawyer_id>', methods=['POST', 'GET'])
@login_required
def profile(lawyer_id):
    user = db.session.execute(db.Select(User).where(User.id == current_user.get_id())).scalar()
    lawyer = db.get_or_404(Lawyer, lawyer_id)
    if request.method == 'POST':
        if user.id == lawyer.user_id:
            # Approving Reviews
            # Checking if the lawyer profile belongs to the current user
            try:
                ratings = db.session.execute(db.select(Rating).where(Rating.lawyer_id == lawyer_id, Rating.author_id == request.form['approve'])).scalar()
                ratings.verified = True
                lawyer.verified_sum = lawyer.verified_sum + ratings.rating
                lawyer.verified_count = lawyer.verified_count + 1
            except:
                # If the user is not approved remove from list
                ratings = db.session.execute(db.select(Rating).where(Rating.lawyer_id == lawyer_id, Rating.author_id == request.form['delete'])).scalar()
                lawyer.verified_sum = lawyer.verified_sum + ratings.rating
                lawyer.verified_count = lawyer.verified_count + 1
                db.session.delete(ratings)
            db.session.commit()
        else:
            # Adding/Editing Reviews
            edit_rating = db.session.execute(db.select(Rating).where(Rating.author_id == user.id)).scalar()
            if edit_rating:
                # If edit_rating exists (Old Review), update the rating values and make the verified status as False
                edit_rating.rating = int(request.form['rating_value'])
                edit_rating.review = request.form['review']
                edit_rating.title = request.form['title']
                edit_rating.rating_author = current_user
                edit_rating.lawyer = lawyer
                edit_rating.rating_date = date.today().strftime("on %d %B %Y")
                edit_rating.verified = False
                db.session.commit()
            else:
                # If edit_rating doesn't exist (No Reviews by this user for this lawyer), add a new rating
                new_rating = Rating(
                    rating=request.form['rating_value'],
                    review=request.form['review'],
                    title=request.form['title'],
                    rating_author=current_user,
                    lawyer=lawyer,
                    rating_date=date.today().strftime("on %d %B %Y")
                )
                db.session.add(new_rating)
                db.session.commit()
        return redirect(url_for('profile', lawyer_id=lawyer_id))
    # Sending lawyer, user, rating data to profile page
    return render_template('profile.html', lawyer=lawyer, user=user, rating_dict=rating_dict)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/openchat')
@login_required
def openchat():
    global chats, names, msgs
    retrieve_chat()
    usernames = []
    for name in names:
        usernames.append(name[:-1].replace('(Lawyer)', ''))

    users = []
    for username in usernames:
        user = db.session.execute(db.Select(User).where(User.username == username)).scalar()
        users.append(user)
    return render_template('openchat.html', user=current_user, names=names, msgs=msgs, n=len(names), users=users, admins=admins)


@socketio.on('chat')
def handle_chat_event(json, methods=['POST', 'GET']):
    # print('received chat: ' + str(json))
    try:
        # Checking if the received event is a chat
        # Write to chat.txt in a 'name: msg' format
        with open('Chat History/chat.txt', mode='a') as file:
            file.write(f"{json['user_name']}: {json['message']}\n")
    except KeyError:
        # Received event is not a chat event
        pass
    socketio.emit('response', json)
    return redirect(url_for('openchat'))


@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    matching_lawyers = db.session.execute(db.select(Lawyer)).scalars()
    lawyer = db.session.execute(db.select(Lawyer).where(Lawyer.id == 1)).scalars()
    if request.method == 'POST':
        name_query = text('')
        bar_id_query = text('')
        expertise_query = text('')
        rating_query = 0
        budget_query = text('')
        experience_query = text('')
        win_query = 0
        location_query = text('')
        if request.form['name']:
            name_query = request.form['name']
        if request.form['bar_council_id']:
            bar_id_query = text(f"Lawyer.bar_council_id == '{request.form['bar_council_id']}'")
        if request.form['case']:
            expertise_query = text(f"Lawyer.expertise == '{request.form['case']}'")
        if request.form['rating']:
            rating_query = int(request.form['rating'])
        if request.form['budget']:
            budget_query = text(f"lawyer.fee <= '{request.form['budget']}'")
        if request.form['experience']:
            experience_query = text(f"Lawyer.experience >= '{int(request.form['experience'])}'")
        if request.form['win']:
            win_query = int(request.form['win'])
        if request.form['location']:
            location_query = request.form['location']

        print(budget_query)
        matching_lawyers = db.session.query(Lawyer).filter(Lawyer.name.like(f"%{name_query}%"), bar_id_query, expertise_query, Lawyer.verified_sum/(Lawyer.verified_count+0.1) >= rating_query, budget_query, experience_query, Lawyer.won/(Lawyer.lost+Lawyer.won)*100 >= win_query, Lawyer.location.like(f"%{location_query}%"))

    return render_template('search.html', matching_lawyers=matching_lawyers, lawyer=lawyer, rating_dict=rating_dict)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/delete_profile', methods=['POST', 'GET'])
@login_required
def delete_profile_caller():
    user = db.session.execute(db.Select(User).where(User.id == current_user.get_id())).scalar()
    lawyer = db.session.execute(db.Select(Lawyer).where(Lawyer.user_id == current_user.get_id())).scalar()
    if user.id == lawyer.user_id:
        delete_profile(request.form['delete'])
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/admin', methods=['POST', 'GET'])
@admin_only
def admin():
    matching_lawyers = db.session.execute(db.select(Lawyer)).scalars()
    lawyer = db.session.execute(db.select(Lawyer).where(Lawyer.id == 1)).scalar()
    if request.method == 'POST':
        try:
            try:
                # Lawyer Verified
                lawyer = db.session.execute(db.select(Lawyer).where(Lawyer.id == request.form['approve'])).scalar()
                lawyer.verified = True
            except:
                # Lawyer Unverified
                lawyer = db.session.execute(db.select(Lawyer).where(Lawyer.id == request.form['no'])).scalar()
                lawyer.verified = False
        except:
            # Deleting Lawyer
            delete_profile(request.form['delete'])
        db.session.commit()
        matching_lawyers = db.session.execute(db.select(Lawyer)).scalars()
    return render_template('admin.html', matching_lawyers=matching_lawyers, rating_dict=rating_dict)


@app.route('/contact', methods=['POST', 'GET'])
@login_required
def contact():
    if request.method == 'POST':
        name = request.form['name']
        sender_email = request.form['email']
        phone = request.form['phone']
        msg_body = request.form['message']
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = to_email
        msg['Subject'] = f'Lawlink Contact Message From: {name}'
        # Email body
        body = f'Email:{sender_email}\nPhone: {phone}\nMessage:\n{msg_body}'
        # Attach body to the message
        msg.attach(MIMEText(body, 'plain'))
        # Establish a connection to Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # Login to Gmail
        server.login(smtp_email, smtp_password)
        # Send email
        server.sendmail(smtp_email, to_email, msg.as_string())
        # Close the SMTP server connection
        server.quit()
    return render_template('contact.html', user=current_user)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
