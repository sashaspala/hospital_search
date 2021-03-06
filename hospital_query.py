from flask import *
from hospital_search import hos_search, format_date
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import shelve
import requests
import sys

app = Flask(__name__)
app.secret_key = '12345'

client = Elasticsearch()
s = Search(using=client, index="review_index")
b = Search(using=client, index="business_index")

review_path = sys.argv[1]
hospital_path = sys.argv[2]

@app.route("/")
def search():
    return render_template('page_1.html')


@app.route('/results', defaults={'page': 1}, methods=['POST', 'GET'])
@app.route('/results/<int:page>/', methods=['POST', 'GET'])
def results(page):
    if request.method == "POST":
        print "post"  # debug
        textq = request.form['textq']
        date_min = request.form['date_min']
        date_max = request.form['date_max']
        stars_min = request.form['stars_min']
        stars_max = request.form['stars_max']
        miles = request.form['miles']
        city = request.form['city']
        state = request.form['state']
        # print hos_search(s, textq, date_min, date_max, stars_min, stars_max)
        init_results = hos_search(s, textq, format_date(date_min), format_date(date_max), stars_min,
                                               stars_max)
        hospital_names = []
        if len(miles) > 0 and (len(city) > 0 or len(state) > 0):
            data = shelve.open(hospital_path)
            final_results = []

            for review in init_results:
                # (review_id, [review ids of same hospital])
                info = data[str(review[0])]
                #these load the review and the other reviews associated with the same hospital

                if get_distance(city + ',' + state, str(info['city']) + ',' + str(info['state'])) > float(miles):
                    final_results.append(review)
                    hospital_names.append(info['name'])
            print(str(final_results))
            data.close()
        else:
            final_results = init_results
            data = shelve.open(hospital_path)
            for review in init_results:
                info = data[str(review[0])]
                hospital_names.append(info['name'])

        session['search_results'] = final_results
        session['hospitals'] = hospital_names

        session['queries'] = [textq, date_min, date_max, stars_min, stars_max, miles]

    top10 = session['search_results'][page*10-10:page*10]
    top10_hosp = session['hospitals'][page*10-10:page*10]
    print top10  # debug
    empty = len(top10) == 0
    prev_button = bool(page > 1)
    next_button = bool(page < (len(session['search_results']) - 1) // 10 + 1)
    query = ", ".join([q for q in session['queries'] if len(q) > 0])
    return render_template('page_2.html', results=top10, hospitals=top10_hosp, empty=empty, prev_button=prev_button, queries=session['queries'],
                           next_button=next_button, page=page, query=query, num_res=len(session['search_results']))
    # return render_template('page_2.html', results=results)

def get_distance(loc_1, loc_2):
    r = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?'
                       'units=imperial&origins={}&destinations={}&key=AIzaSyDDpG7Xixqmq_O1FZNN7LKICP82gAdZT08'.format(loc_1, loc_2))
    print(r)
    print(r.json()['rows'][0])
    return float(r.json()['rows'][0]['elements'][0]['distance']['value']) / 1609.34

@app.route('/<business_id>/<review_id>')
def show_info(business_id, review_id):

    data = shelve.open(review_path)
    review = data[str(review_id)]["text"]
    data.close()

    hos_data = shelve.open(hospital_path)
    info = hos_data[str(business_id)]
    hos_data.close()
    return render_template('page_3.html', hos_name=info["name"], review=review, info=info)

@app.route('/<business_id>')
def hos_info(business_id):
    hos_data = shelve.open(hospital_path)
    info = hos_data[str(business_id)]
    hos_data.close()
    return render_template('page_3.html', hos_name=info["name"], info=info)


if __name__ == "__main__":
    app.run()
