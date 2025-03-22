from pydantic import BaseModel

class QuerySong(BaseModel):
    query: str