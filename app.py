from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_mail import Mail, Message
import secrets
import re
import os

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'example@gmail.com')
if not app.config['MAIL_USERNAME']:
    raise ValueError("MAIL_USERNAME environment variable is not set")

app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'aaaa bbbb cccc dddd')
if not app.config['MAIL_PASSWORD']:
    raise ValueError("MAIL_PASSWORD environment variable is not set")

# Initializing Flask-Mail
mail = Mail(app)


def process_contact_form():
    errors = []

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    subject = request.form.get('subject', '').strip()
    message_content = request.form.get('message', '').strip()

    if not name:
        errors.append("Name is required.")

    if not email:
        errors.append("Email is required.")

    if not subject:
        subject = "General Inquiry"

    if not message_content:
        errors.append("Message is required.")

    if name and not re.match(r"^[A-Za-z\s]+$", name):
        errors.append("Name should only contain letters and spaces.")

    if email and not re.match(
        r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        email
    ):
        errors.append("Please enter a valid email address.")

    if message_content and (len(message_content) < 10 or len(message_content) > 500):
        errors.append("Message must be between 10 and 500 characters.")

    if errors:
        return False, errors

    try:
        msg = Message(
            subject=f"{subject} | nayab.dev",
            sender=app.config['MAIL_USERNAME'],
            recipients=['nayab.webdeveloper@gmail.com'],
            body=f"""
                Name: {name}
                Email: {email}

                Message:
                {message_content}
                """,
            reply_to=email
        )

        mail.send(msg)
        return True, None

    except Exception as e:
        app.logger.error(f"Contact form error: {str(e)}")
        return False, ["Failed to send message. Please try again later."]
    
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    return response

@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml")



@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        success, errors = process_contact_form()

        if success:
            flash("Thank you for your message! I'll get back to you soon.", "success")
        else:
            flash(" ".join(errors), "danger")

        return render_template('index.html', section='contact')

    return render_template('index.html')

@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        success, errors = process_contact_form()

        if success:
            flash("Thank you for your message! I'll get back to you soon.", "success")
        else:
            flash(" ".join(errors), "danger")

        return render_template('contact.html', section='contact')

    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)