def get_response_type(data):
    
    types = set()

    for field, value in data.items():
        if field.startswith("title") or field.startswith("description"):
            types.add("course")
        elif field.startswith("detail.category"):
            types.add(f"category-{value}")
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

    title = get_title(source_data, type)
    description = get_description(source_data, type)
    url = get_cta_url(type, title, id)

    # Handle 'category' type with a list of items
    if type.startswith("category"):
        categories = source_data["detail"][type.split("-")[0]]
        _category = type.split("-")[1].replace("<em>", "").replace("</em>", "")
        # Create a list of DTOs for each category
        res = []
        for category in categories :
            if category.get("title", "") and category.get("title") in _category:
                res.append({
                        "title": category.get("title", ""),
                        "description": "category",
                        "url": get_cta_url(type, category.get("title", ""), id)
                    })
        return res 

    # Return a single DTO for types other than 'category'
    return {
        "title": title,
        "description": description,
        "url": url
    } if title else {}