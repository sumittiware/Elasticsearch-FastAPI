import fastapi 
from database.elastic_search_client import *
from utils.utils import *

app = fastapi.FastAPI()


@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/search")
async def search(query:str = None, state:str = None, response: fastapi.Response = None):
    state = "submitted" if state is None else state
    elastic_client = get_elasticsearch_client()

    if query is None :
        response.status_code = fastapi.status.HTTP_400_BAD_REQUEST
        return {"message": "No query provided"}
    
    if state == "submitting" :
        
        elastic_search_response = elastic_client.search(index=search_index, body=get_submitting_query(query))

        response_hits = elastic_search_response["hits"]["hits"]

        if len(response_hits) == 0 :
            response.status_code = fastapi.status.HTTP_404_NOT_FOUND
            return {"message": "No matching documents found"}
        
        response.status_code = fastapi.status.HTTP_200_OK

        search_responses = []

        for hit in response_hits :
            # first I will get the type if the response
            types = get_response_type(hit["highlight"])
            # then I will create a response based on type 
            for type in types:
                 search_response = get_search_response_data(type=type, data=hit)
                 search_responses.append(search_response)
            
        final_response = process_search_response(search_responses)
        return { 
                "status":"ok", 
                "data" : final_response
            } 
    else :
        elastic_search_response = elastic_client.search(index=search_index, body=get_submitted_query(query))
        
        response_hits = elastic_search_response["hits"]["hits"]

        course_ids = []

        for hit in response_hits :
             course_ids.append(hit["_id"])

        course_response = elastic_client.search(index=course_index, body=get_course_query(course_ids))

        course_response_hits = course_response["hits"]["hits"]

        courses = []

        for hit in course_response_hits :
            course_hit = hit["_source"]

            course_data = {
                "id": hit["_id"],
                "title": course_hit["name"],
                "description": course_hit["description"],
                "type": course_hit["type"],
                "banners" : course_hit["banners"],
            }

            courses.append(course_data)

        return {"status":"ok","data" : courses}


def process_search_response(data):
    categories_seen = set()
    processed_data = []

    # First, process categories to ensure uniqueness
    for item in data:
        if isinstance(item, list):  # Assuming lists contain categories
            for category in item:
                title = category["title"]
                if title not in categories_seen:
                    categories_seen.add(title)
                    processed_data.append({"type": "category", **category})

    # Then, process courses and instructors
    for item in data:
        if isinstance(item, dict):  # Assuming dicts are courses or instructors
            if item["description"] == "category":
                continue  # Skip categories in this pass
            item_type = "course" if "course" in item["url"] else "instructor"
            processed_data.append({"type": item_type, **item})

    # Sort the data: categories -> courses -> instructors
    type_order = {"category": 1, "course": 2, "instructor": 3}
    processed_data.sort(key=lambda x: type_order[x["type"]])

    return processed_data


if __name__ == "__main__":
        print("Starting server at port 8000")