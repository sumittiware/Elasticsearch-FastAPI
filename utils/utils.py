def get_response_type(data):
    types = set()
    findings = data.keys()

    for field in findings:
        if field.startswith("title") or field.startswith("description"):
            types.add("course")
        elif field.startswith("detail.category"):
            types.add("category")
        elif field.startswith("detail.instructor"):
            types.add("instructor")
    
    return types

def get_cta_url(type: str, query: str, course_id: int):
    if type == "course":
        url = f"/course/detail/{course_id}"
    else:
        url = f"/search?q={query}"
    
    return url


def get_title(data, type):
    if type == "course":
        return data["title"]
    elif type == "instructor":
        return data["detail"][type]["title"]
    elif type == "category":
        pass
   
    return None

def get_description(data, type):
    if type == "course":
        return data.get("description", "")
    return type 

def get_search_response_data(type: str, **data,):
    id = data["data"]["_id"]
    source_data = data["data"]["_source"]
    highlight = data["data"]["highlight"]

    title = get_title(source_data, type)
    description = get_description(source_data, type)
    url = get_cta_url(type, title, id) if title else None

   

    # Return a single DTO for types other than 'category'
    return {
        "title": title,
        "description": description,
        "url": url
    } if title else {}