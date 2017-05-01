import json
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import *
from elasticsearch_dsl.connections import connections


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


# Creates index
if __name__ == "__main__":
    # Connect to elasticsearch
    es = Elasticsearch()
    connections.create_connection(hosts=['localhost'])
    # Get reviews
    corpus = open('hospitals_reviews.json')
    reviews = json.load(corpus)

    review_index = Index('review_index')
    if review_index.exists():
        review_index.delete()  # overwrite any previous version
    review_index.doc_type(Review)
    review_index.create()

    # Actions for bulk loading
    actions = [
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

    helpers.bulk(es, actions)
    corpus.close()

    # Check that mapping is correct
    print review_index._get_mappings()

    # Test that index is filled
    print es.get(index='review_index', doc_type='review', id="Mc86JBqffWrg9hH4EKAwug")  # debug