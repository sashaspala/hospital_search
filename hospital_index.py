import json
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import *
from elasticsearch_dsl.connections import connections
import shelve


class Review(DocType):
    # IDs shouldn't need any type of processing
    business_id = Text()
    user_id = Text()
    # Maybe for filters?
    useful = Integer()
    stars = Integer()
    # The only field that really needs processing
    text = Text(analyzer='snowball')  # refine later
    date = Date()

    class Meta:
        index = 'review_index'

    def save(self, **kwargs):
        return super(Review, self).save(**kwargs)

class Business(DocType):
    business_id = Text()
    name = Text()

    city = Text()
    state = Text()
    review_count = Integer()

    class Meta:
        index = 'business_index'

    def save(self, **kwargs):
        return super(Review, self).save(**kwargs)

# Creates index
if __name__ == "__main__":
    # Connect to elasticsearch
    es = Elasticsearch()
    connections.create_connection(hosts=['localhost'])
    # Get reviews
    corpus = open('expanded_reviews_5000.json')
    business_corpus = open('expanded_dataset.json')

    reviews = json.load(corpus)
    businesses = json.load(business_corpus)

    review_index = Index('review_index')
    business_index = Index('business_index')

    if review_index.exists():
        review_index.delete()  # overwrite any previous version
    if business_index.exists():
        business_index.delete()

    review_index.doc_type(Review)
    review_index.create()

    business_index.doc_type(Business)
    business_index.create()

    # Actions for bulk loading
    review_actions = [
        {
            "_index": "review_index",
            "_id": reviews[i]["review_id"],
            "_type": "review",
            "_source": {
                "business_id": reviews[i]["business_id"],  # hospital
                "stars": reviews[i]["stars"],  # stars given
                "useful": reviews[i]["useful"],  # number of people who found the review useful
                "user_id": reviews[i]["user_id"],  # user who posted review
                "text": reviews[i]["text"],  # text of review
                "date": reviews[i]["date"]
            }
        }
        for i in range(len(reviews))
        ]

    business_actions = [
        {
            "_index": "business_index",
            "_id": businesses[i]["business_id"],
            "_type": "business",
            "_source": {
                "business_id": businesses[i]["business_id"],
                "name": businesses[i]['name'],
                "city": businesses[i]['city'],
                "state": businesses[i]['state'],
                "review_count": businesses[i]['review_count']
            }
        }
        for i in range(len(businesses))
    ]

    helpers.bulk(es, review_actions)

    # Create index for easy retrieval of reviews
    id_to_data = shelve.open('IDtoData.dat', flag='n')
    id_to_data['favicon.ico'] = ''  # Don't know why, but it keeps looking for this and raising key errors
    for review in reviews:
        id_to_data[str(review["review_id"])] = review
    id_to_data.close()

    helpers.bulk(es, business_actions)
    business_corpus.close()
    corpus.close()

    # Check that mapping is correct
    print review_index._get_mappings()

    # Test that index is filled
    print es.get(index='review_index', doc_type='review', id="Mc86JBqffWrg9hH4EKAwug")  # debug
