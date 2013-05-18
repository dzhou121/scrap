from flask import Flask, render_template, request, jsonify
from scrap import scraper

app = Flask(__name__)


@app.route('/')
def index():
    """ The index page of the web app """
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """ The search page to get the link results, will return json reponse """
    keyword = request.form['keyword']
    domain = request.form['domain']
    search_engine = request.form['search_engine']
    scraper_class_name = '%sScraper' % search_engine.strip().capitalize()
    scraper_class = getattr(scraper, scraper_class_name)
    scraper_obj = scraper_class(keyword, domain)
    links = scraper_obj.get_links()
    return jsonify(links=links)
