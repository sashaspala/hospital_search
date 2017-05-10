from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
from collections import defaultdict
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer


# Builds query
def hos_search(searchobj, textq, date_min, date_max, stars_min, stars_max, miles, zip_code):
    stem = WordNetLemmatizer()
    if len(textq) > 0:
        terms = textq.split()
        must = [Q('match', text=term) for term in terms]
        should = []
        # Get related words that might increase usefulness
        for q in terms:
            if q.endswith("'s"):  # mostly for terms like "children's"
                q = q[:-2]
            try:
                ss = wordnet.synsets(stem.lemmatize(q))[0]
                print [str(word.name()).split(".")[0] for word in ss.hyponyms() if "_" not in word.name()]
                should += [str(word.name()).split(".")[0] for word in ss.hyponyms() if "_" not in word.name()]
            except IndexError:
                continue
        should = [Q('match', text=term) for term in should]
        searchobj.query = Q('bool', must=must, should=should)
    else:
        searchobj.query = Q()

    # Filter by date if present
    if len(date_min) > 0:
        if len(date_max) > 0:
            searchobj = searchobj.filter("range", date={"gte": date_min, "lte": date_max, "format": "yyyy-MM-dd"})
        else:
            searchobj = searchobj.filter("range", date={"gte": date_min, "format": "yyyy-MM-dd"})
    else:
        if len(date_max) > 0:
            searchobj = searchobj.filter("range", date={"lte": date_max, "format": "yyyy-MM-dd"})

    # Filter by number of stars if present
    if len(stars_min) > 0:
        if len(stars_max) > 0:
            searchobj = searchobj.filter("range", stars={"gte": int(stars_min), "lte": int(stars_max)})
        else:
            searchobj = searchobj.filter("range", stars={"gte": int(stars_min)})
    else:
        if len(stars_max) > 0:
            searchobj = searchobj.filter("range", stars={"lte": int(stars_max)})

    # Run query
    respobj = searchobj.scan()
    ret = [(r.meta.id, r["business_id"]) for r in respobj]
    print ret  # debug
    return group_hospitals(ret)


def group_hospitals(reviews):
    hos_dict = defaultdict(list)
    for (rev_id, bus) in reviews:
        hos_dict[bus].append(rev_id)
    return [(k, hos_dict[k]) for k in hos_dict]


def format_date(date_str):
    if len(date_str) == 0:
        return date_str
    date_str = date_str.replace("/", "-")
    pieces = date_str.split("-")
    if 2018 > int(pieces[0]) > 1900:  # YYYY/MM/DD
        return date_str
    if 0 < int(pieces[0]) < 13:  # MM/DD/YYYY
        return "-".join([pieces[2], pieces[0], pieces[1]])
    if 0 < int(pieces[0]) < 32:  # DD/MM/YY
        return "-".join([pieces[2], pieces[1], pieces[0]])
    return ""

if __name__ == "__main__":
    # Test search function
    client = Elasticsearch()
    connections.create_connection(hosts=['localhost'])
    s = Search(using=client, index="review_index")
    print hos_search(s, "children's hospitals", "2015-12-20", "", "", "", "", "")
    # print(format_date("12-14-2017"))
    # print(format_date("18-11-2017"))
    # print(format_date("2017-10-11"))
    # print(format_date("00-00-0000"))
