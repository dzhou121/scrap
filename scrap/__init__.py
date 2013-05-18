from flask import Flask, render_template, request
from scrap import scraper

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    links = []
    keyword = ''
    domain = ''
    if request.method == 'POST':
        keyword = request.form['keyword']
        domain = request.form['domain']
        google_scraper = scraper.GoogleScraper(keyword, domain)
        links = google_scraper.get_links()
    return render_template('index.html',
                           links=links,
                           keyword=keyword,
                           domain=domain)


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
