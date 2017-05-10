from flask import *
from business_search import busi_search
from hospital_search import hos_search, format_date
from geopy.distance import vincenty
from geopy.geocoders import Nominatim
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
        #session['search_results'] = # [result for result in init_results
                                     #if get_distance(locator, (city, state), (result['city'], result['state'])) < float(miles)]
        if len(miles) > 0 and (len(city) > 0 or len(state) > 0):
            locator = Nominatim()
            final_results = []
            for index in range(len(init_results)):
                print(init_results[1][index])
                #these load the review and the other reviews associated with the same hospital
                print(init_results[index][1]['city'])
                print(init_results[index][1]['state'])
                if get_distance(locator, (city, state), (init_results[index][1]['city'], init_results[index][1]['state'])) > float(miles):
                    final_results.append(init_results[index][0])
        else:
            final_results = init_results
        session['search_results'] = final_results
        #print session['search_results']
        session['queries'] = [textq, date_min, date_max, stars_min, stars_max, miles]
    top10 = session['search_results'][page*10-10:page*10]
    print top10  # debug
    empty = len(top10) == 0
    prev_button = bool(page > 1)
    next_button = bool(page < (len(session['search_results']) - 1) // 10 + 1)
    query = ", ".join([q for q in session['queries'] if len(q) > 0])
    return render_template('page_2.html', results=top10, empty=empty, prev_button=prev_button, queries=session['queries'],
                           next_button=next_button, page=page, query=query, num_res=len(session['search_results']))
    # return render_template('page_2.html', results=results)


def get_distance(locator, loc_1, loc_2):
    loc_1_point = locator.geocode(loc_1[0] + ' , ' + loc_1[1])
    loc_2_point = locator.geocode(loc_2[0] + ' , ' + loc_2[1])

    return vincenty((loc_1_point.latitude, loc_1_point.longitude), (loc_2_point.latitude, loc_2_point.longitude)).miles

@app.route('/<business_id>/<review_id>')
def show_info(business_id, review_id):

    data = shelve.open("IDtoData.dat")
    review = data[str(review_id)]["text"]
    data.close()

    hos_data = shelve.open("IDtoData.dat")
    info = hos_data[str(business_id)]
    hos_data.close()
    return render_template('page_3.html', hos_name=hos_data["name"], review=review, info=info)

@app.route('/<business_id>')
def hos_info(business_id):
    hos_data = shelve.open("IDtoData.dat")
    info = hos_data[str(business_id)]
    hos_data.close()
    return render_template('page_3.html', hos_name=hos_data["name"], review=review, info=info)


if __name__ == "__main__":
    app.run()
