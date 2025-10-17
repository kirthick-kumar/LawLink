from flask import render_template, request, flash
from flask_login import login_required, current_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
smtp_email = 'lawlinkotp@gmail.com'
smtp_password = 'hkvcjhlajwemyive'
to_email = 'lawlinkotp@gmail.com'

def send_contact_email(name, sender_email, phone, message):
    """Send contact form message via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = to_email
        msg['Subject'] = f'Lawlink Contact Message From: {name}'
        
        # Email body
        body = f'Name: {name}\nEmail: {sender_email}\nPhone: {phone}\nMessage:\n{message}'
        
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
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@login_required
def contact():
    """
    Handle contact form submissions
    GET: Display contact form
    POST: Process contact form and send email
    """
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        sender_email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        msg_body = request.form.get('message', '').strip()
        
        # Validate form data
        if not name or not sender_email or not msg_body:
            flash('Please fill in all required fields (Name, Email, and Message)', 'error')
            return render_template('contact.html', user=current_user)
        
        # Send email
        if send_contact_email(name, sender_email, phone, msg_body):
            flash('Your message has been sent successfully! We will get back to you soon.', 'success')
        else:
            flash('There was an error sending your message. Please try again later.', 'error')
        
        return render_template('contact.html', user=current_user)
    
    # GET request - just display the form
    return render_template('contact.html', user=current_user)