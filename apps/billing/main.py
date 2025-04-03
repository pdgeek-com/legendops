from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return f'Hello from {__name__}!'

if __name__ == '__main__':
    app.run(debug=True)
