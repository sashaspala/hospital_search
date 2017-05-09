from flask import *
from hospital_search import hos_search, format_date
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import shelve

app = Flask(__name__)
app.secret_key = '12345'

client = Elasticsearch()
s = Search(using=client, index="review_index")


@app.route("/")
def search():
    return render_template('page_1.html')


@app.route('/results', defaults={'page': 1}, methods=['POST', 'GET'])
@app.route('/results/<int:page>/', methods=['POST', 'GET'])
def results(page):
    if request.method == "POST":
        print "post"  # debug
        textq = request.form['textq']
        print textq
        date_min = request.form['date_min']
        date_max = request.form['date_max']
        stars_min = request.form['stars_min']
        stars_max = request.form['stars_max']
        miles = request.form['miles']
        zip_code = request.form['zip_code']
        # print hos_search(s, textq, date_min, date_max, stars_min, stars_max)
        session['search_results'] = hos_search(s, textq, format_date(date_min), format_date(date_max), stars_min,
                                               stars_max, miles, zip_code)
        print session['search_results']
        session['queries'] = [textq, date_min, date_max, stars_min, stars_max, miles, zip_code]
    top10 = session['search_results'][page*10-10:page*10]
    print top10  # debug
    empty = len(top10) == 0
    prev_button = bool(page > 1)
    next_button = bool(page < (len(session['search_results']) - 1) // 10 + 1)
    query = ", ".join([q for q in session['queries'] if len(q) > 0])
    return render_template('page_2.html', results=top10, empty=empty, prev_button=prev_button, queries=session['queries'],
                           next_button=next_button, page=page, query=query, num_res=len(session['search_results']))
    # return render_template('page_2.html', results=results)


@app.route('/<review_id>')
def show_info(review_id):
    data = shelve.open("IDtoData.dat")
    info = data[str(review_id)]
    data.close()
    return render_template('page_3.html', id=review_id, info=info)


if __name__ == "__main__":
    app.run()
