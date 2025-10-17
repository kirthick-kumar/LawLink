from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

# Email configuration
smtp_email = 'lawlinkotp@gmail.com'
smtp_password = 'hkvcjhlajwemyive'
otp_storage = {}

def send_otp_email(user_email, otp):
    """Send OTP email to user"""
    try:
        msg = MIMEText(f'Email: {user_email} has been used to register to LawLink Website, please enter the otp mentioned below into the signup form to verify the email\nOTP: {otp}')
        msg['Subject'] = 'LawLink OTP'
        msg['From'] = smtp_email
        msg['To'] = user_email
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, user_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        log_user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if log_user:
            # To check if email and password are both correct
            if log_user.password == password:
                login_user(log_user)
                # Remove flash message to prevent duplicates
                if hasattr(log_user, 'lawyer') and log_user.lawyer:
                    return redirect(url_for('profile', lawyer_id=log_user.lawyer.id))
                else:
                    return redirect(url_for('search'))
            else:
                flash('Invalid Password', 'error')
        else:
            flash('Invalid Email', 'error')
    return render_template('login.html')

def signup():
    if request.method == 'POST':
        name = request.form['name']
        user_email = request.form['email']
        user_password = request.form['password']

        otp = random.randint(100000, 999999)
        if send_otp_email(user_email, otp):
            otp_storage[user_email] = otp
            return render_template('otp.html', name=name, user_email=user_email, user_password=user_password)
        else:
            flash('Error sending OTP email', 'error')
    
    return render_template('signup.html')

def verify_otp():
    if request.method == 'POST':
        name = request.form['name']
        user_email = request.form['email']
        user_password = request.form['password']
        
        try:
            lawyer = request.form['lawyer']
        except:
            lawyer = 'off'
            
        stored_otp = otp_storage.get(user_email)
        if stored_otp and int(request.form['otp']) == stored_otp:
            try:
                user = User(username=name, email=user_email, password=user_password)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                # Add welcome message only on signup, not login
                flash(f'Welcome to LawLink, {name}!', 'success')
                
                if lawyer == 'on':
                    return redirect(url_for('profile_edit'))
                else:
                    return redirect(url_for('search'))
            except Exception as e:
                flash('Email already registered to LawLink', 'error')
                return redirect(url_for('login'))
        else:
            flash('Invalid OTP', 'error')
            return render_template('otp.html', name=name, user_email=user_email, user_password=user_password)

    return redirect(url_for('signup'))

def logout():
    logout_user()
    return redirect(url_for('home'))