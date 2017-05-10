from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections


# Builds query
def busi_search(searchobj, business_id):
    searchobj.query = Q('match', business_idt=business_id)

    # Run query
    respobj = searchobj.scan()
    return respobj

if __name__ == "__main__":
    # Test search function
    client = Elasticsearch()
    connections.create_connection(hosts=['localhost'])
    s = Search(using=client, index="review_index")
    #print busi_search(s, )
