



def get_cta_url(type: str, query: str, course_id: int):
    if type == "course":
        url = f"/course/detail/{course_id}"
    else:
        url = f"/search?q={query}"
    
    return url

