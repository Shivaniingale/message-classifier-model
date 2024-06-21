from flask import Flask, request, render_template, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import joblib
import pandas as pd
import asyncio
from telethon.sync import TelegramClient
from telethon import functions, types

# Load the trained model
model = joblib.load('message_classifier.pkl')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create the database
with app.app_context():
    db.create_all()

# Define the TelegramMessageFetcher class
class TelegramMessageFetcher:
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient('session_name', api_id, api_hash)

    async def connect_to_telegram(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(input('Enter your phone number (including country code): '))
            await self.client.sign_in(input('Enter the code: '))

    async def fetch_messages(self, username):
        messages = []
        try:
            chat = await self.client.get_entity(username)
            async for message in self.client.iter_messages(chat, reverse=True):
                sender = message.sender_id
                text = message.text
                date = message.date
                if text:  # Ensure we only append messages with text
                    messages.append({"Sender": sender, "message": text, "Date": date})
        except Exception as e:
            print(f"An error occurred: {e}")
        return messages

    async def disconnect_from_telegram(self):
        await self.client.disconnect()

    async def save_messages_to_csv(self, messages, filename):
        if messages:  # Check if messages list is not empty
            df = pd.DataFrame(messages, columns=["Sender", "message", "Date"])
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d %H:%M:%S')
            df.to_csv(filename, index=False)
            print(f"Messages saved to {filename}")
        else:
            print("No messages to save")

API_ID = 20815381
API_HASH = '8882005290fa97208a103d243c864f9f'
message_fetcher = TelegramMessageFetcher(API_ID, API_HASH)

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])  # Specify allowed methods
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        df = pd.read_csv(file)

        # Ensure all messages are strings
        df['message'] = df['message'].astype(str)

        prediction = model.predict(df['message'])
        df['prediction'] = ['Unsafe' if p == 1 else 'Safe' for p in prediction]
        results = df.to_dict(orient='records')
        return render_template('index.html', results=results)
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    message = request.form['message']

    # Ensure the message is a string
    if isinstance(message, (int, float)):
        message = str(message)

    prediction = model.predict([message])[0]
    output = 'Safe' if prediction != 1 else 'Unsafe'
    return render_template('index.html', prediction_text=f'The message is: {output}')

@app.route('/fetch_messages', methods=['GET', 'POST'])
@login_required
def fetch_messages():
    if request.method == 'POST':
        contact_username = request.form['username']
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(message_fetcher.connect_to_telegram())
        messages = loop.run_until_complete(message_fetcher.fetch_messages(contact_username))
        print(f"Fetched messages: {messages}")  # Logging fetched messages
        loop.run_until_complete(message_fetcher.disconnect_from_telegram())
        loop.run_until_complete(message_fetcher.save_messages_to_csv(messages, f"{contact_username}_messages.csv"))
        return send_file(f"{contact_username}_messages.csv", as_attachment=True)
    return render_template('fetch_messages.html')

if __name__ == '__main__':
    app.run(debug=True)
