from flask import Flask, render_template
from flask.ext import restful
from scrap.api import scraper

app = Flask(__name__)
api = restful.Api(app)


@app.route('/')
def index():
    """ The index page of the web app """
    return render_template('index.html')

api.add_resource(scraper.API, '/search/<string:params>')
