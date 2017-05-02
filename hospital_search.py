from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections


# Builds query
def hos_search(searchobj, textq, date_min, date_max, stars_min, stars_max):
    if len(textq) > 0:
        searchobj.query = Q('match', text=textq)
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
    ret = [r.meta.id for r in respobj]
    print ret  # debug
    return ret

if __name__ == "__main__":
    # Test search function
    client = Elasticsearch()
    connections.create_connection(hosts=['localhost'])
    s = Search(using=client, index="review_index")
    print hos_search(s, "", "2015-12-20", "", "", "")
