from flask import *
from hospital_search import hos_search
from business_search import busi_search
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import shelve

app = Flask(__name__)
app.secret_key = '12345'

client = Elasticsearch()
s = Search(using=client, index="review_index")
b = Search(using=client, index="business_index")


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
        print hos_search(s, textq, date_min, date_max, stars_min, stars_max)
        session['search_results'] = hos_search(s, textq, date_min, date_max, stars_min, stars_max)
        print session['search_results']
        session['queries'] = [textq, date_min, date_max, stars_min, stars_max]
    top10 = session['search_results'][page*10-10:page*10]
    print top10  # debug
    empty = len(top10) == 0
    prev_button = bool(page > 1)
    next_button = bool(page < (len(session['search_results']) - 1) // 10 + 1)
    query = ", ".join([q for q in session['queries'] if len(q) > 0])
    return render_template('page_2.html', results=top10, empty=empty, prev_button=prev_button, queries=session['queries'],
                           next_button=next_button, page=page, query=query, num_res=len(session['search_results']))
    # return render_template('page_2.html', results=results)


@app.route('/<business_id>/<review_id>')
def show_info(business_id, review_id):

    data = shelve.open("IDtoData.dat")
    info = data[str(review_id)]
    data.close()

    #also now search for the hospital that matches this business_id
    session['hosptial'] = busi_search(b, business_id)[0]
    print(session['hospital'])

    return render_template('page_3.html', id=review_id, info=info)


if __name__ == "__main__":
    app.run()
