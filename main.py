import fastapi 
from database.elastic_search_client import *
from utils.utils import *

app = fastapi.FastAPI()


@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/search")
async def search(query:str = None, state:str = None, result_type:str = None,response: fastapi.Response = None):
    state = "submitted" if state is None else state
    elastic_client = get_elasticsearch_client()
    result_type = "course" if result_type is None else result_type

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
           id = hit["_id"]
           title = hit["_source"]["title"]
           description = hit["_source"]["description"]
           type = hit["_source"]["type"]
           url = get_cta_url(type, title, id)

           search_response = {
               "id": id,
               "title": title,
               "description": description,
               "type": type
           }

           search_responses.append(search_response)
           
            
        return { 
                "status":"ok", 
                "data" : search_responses
            } 
    else :
        elastic_search_response = elastic_client.search(index=search_index, body=get_submitted_query(query,type=result_type))
        
        response_hits = elastic_search_response["hits"]["hits"]

        entity_ids = []

        for hit in response_hits :
             entity_ids.append(hit["_id"])

        entity_response = elastic_client.search(index="search-f{result_type}-dev", body=get_id_query(entity_ids))

        entity_response_hits = entity_response["hits"]["hits"]

        results = []

        for hit in entity_response_hits :
            entity_hit = hit["_source"]

            entity_data = {
                "id": hit["_id"],
                "title": entity_hit["name"],
                "description": entity_hit["description"],
                "type": entity_hit["type"],
                "image" : entity_hit["image"],
                # TODO : This can chnage based on the entity type
                "cta_url": f"/course/detail/{hit['_id']}"
            }

            results.append(entity_data)

        return {
            "status":"ok",
            "type" : result_type,
            "data" : results
        }




if __name__ == "__main__":
        print("Starting server at port 8000")