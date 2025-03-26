import random

from emails.email_functions import *
from fastapi import HTTPException
from functions import *
from tables import *
from spotify.spotify_functions import *
from sql import *
from starlette.middleware.cors import CORSMiddleware
from youtube.youtube_functions import *
from tables import *

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Auralynk"}

@app.post("/user/create", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    salt = random.randint(00000, 99999)
    existing_user = session.query(MainUser).filter(MainUser.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user.password = hash_password(user.password, salt)
    user.salt = salt

    db_user = MainUser.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.get("/user/", response_model=UserPublic)
def get_user(user: VerifyUser, session: SessionDep):
    existing_user = session.query(MainUser).filter(MainUser.email == user.email).first()
    if not existing_user:
        raise HTTPException(status_code=400, detail="Email not registered")
    return existing_user

@app.get('/user/verify')
async def verify_user(user: VerifyUser, session: SessionDep):
    existing_user = session.query(MainUser).filter(MainUser.email == user.email).first()
    if not existing_user:
        raise HTTPException(status_code=400, detail="Email not registered")

    is_password_valid = validate_password(user.password, existing_user.password, existing_user.salt)

    if not is_password_valid:
        raise HTTPException(status_code=400, detail="Password not valid")

    return {"is_password_valid": is_password_valid, "email": existing_user.email, "id": existing_user.id}

@app.patch("/user/update/{user_id}", response_model=UserPublic)
async def update_user(user_id: int, user: UpdateUser, session: SessionDep):
    user_db = session.get(MainUser, user_id)
    user_data = user.model_dump(exclude_unset=True)

    if 'songs' in user_data:
        if user_db.songs is None:
            user_db.songs = []
        current_songs = user_db.songs
        new_songs = user_data['songs']
        user_data['songs'] = current_songs + new_songs

    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

@app.get("/search/tracks")
async def search_songs(query: QuerySong):
    token = get_spotify_token()
    track = spotify_search_track(token, query)
    return {"track": track, "href": track['external_urls']['spotify'], "youtube_track_name": f"{track['name']} - {track['artists'][0]['name']}"}

@app.get("/youtube/search")
async def youtube_search(search: QuerySong):
    result = search_youtube(search.query)
    return {"url": result['link'], "title": result['title']}

@app.post("/email/welcome")
async def email_welcome(email: WelcomeEmail, session: SessionDep):
    does_user_exist = session.query(EmailList).filter(EmailList.email == email.email).first()
    
    if not does_user_exist:
        add_user_to_email_list(email, session)
        
    is_email_sent = send_welcome_email(email.email, email.name)

    if not is_email_sent:
        raise HTTPException(status_code=500, detail="Email not sent")

    return {"message": "Email sent"}