from elasticsearch import Elasticsearch
from config.config import config

search_index = "search-search-dev"
course_index = "search-course-dev"

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


def get_submitting_query(query:str):
    return {
        "query": {
            "query_string": {
                "query": f"*{query}*",
                "default_operator": "AND"
            }
        },
        "highlight": {
            "fields": {
                "*": {}
            }
        }    
    }

def get_submitted_query(query:str):
    return {
        "query": {
            "multi_match": {
                "fields": ["*"],
                "query": query
            }
        },
        "highlight": {
            "fields": {
                "*": {}
            }
        },
        "_source": False
    }

def get_course_query(ids):
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