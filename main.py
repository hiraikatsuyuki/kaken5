from flask import Flask, render_template
from benchmark import benchmark

app = Flask(__name__)


app.register_blueprint(benchmark)

if __name__ == "__main__":
    app.run(debug=True)
