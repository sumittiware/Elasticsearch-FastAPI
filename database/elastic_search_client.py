from elasticsearch import Elasticsearch
from config.config import config

search_index = "search-search-dev"
course_index = "search-course-dev"
categpry_index  = "search-category-dev"
instructor_index = "search-instructor-dev"

class ElasticsearchClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            host = config["elasticsearch"]["host"]
            api_key_encoded = config["elasticsearch"]["api_key_encoded"]
            print(host, api_key_encoded)
            cls._instance = Elasticsearch(host, api_key=api_key_encoded)
        return cls._instance

def get_elasticsearch_client():
    return ElasticsearchClient.get_instance()


def get_submitting_query(query:str, page:int=1, size:int=10):
    return {
        "from": (page - 1) * size,
        "size": size,
        "query": {
            "query_string": {
                "query": f"{query}*",
                "default_operator": "AND",
                "fields": [
                    # Boost the title field
                    "detail.category.title^4",
                    "title^3",
                    "description^2",
                    "detail.instructor.title^1"
                ]
            }
        },
        "highlight": {
            "fields": {
                "*": {}
            }
        }    
    }

def get_submitted_query(query:str,type:str,page:int=1, size:int=10):
    return {
        "from": (page - 1) * size,
        "size": size,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "fields": ["*"],
                        "query": "f{query}*"
                    }
                },
                "filter": {
                    "term": {
                    "result_type": "f{str}"
                    }
                }
            }   
        },
        "highlight": {
            "fields": {
            "*": {}
            }
        },
        "_source": False
    }


def get_id_query(ids):
    return {
        "query": {
            "bool": {
                "filter": {
                    "terms": {
                        "_id": ids
                    }
                }
            }
        }
    }