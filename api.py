import random

from auth import *
from emails.email_functions import *
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
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
async def email_welcome(email: EmailTable, session: SessionDep):
    does_user_exist = session.query(EmailList).filter(EmailList.email == email.email).first()
    
    if not does_user_exist:
        did_add_user = add_user_to_email_list(email, session)
        if did_add_user is None:
            raise HTTPException(status_code=500, detail="Failed to add user to email list")
        
        is_email_sent = send_welcome_email(email.email, email.name)

        if not is_email_sent:
            raise HTTPException(status_code=500, detail="Email not sent")

        return {"message": "Email sent"}
    else:
        raise HTTPException(status_code=400, detail="Email already registered")

@app.post("/email/add")
async def add_email(email: EmailTable, session: SessionDep):
    does_user_exist = session.query(EmailList).filter(EmailList.email == email.email).first()
    print(does_user_exist)
    if not does_user_exist:
        did_add_user = add_user_to_email_list(email, session)
        if did_add_user is None:
            raise HTTPException(status_code=500, detail="Failed to add user to email list")
        
        return did_add_user
    
    raise HTTPException(status_code=400, detail="Email already registered")

@app.get("/email/list")
async def get_email_list(session: SessionDep, current_user: User = Depends(get_current_user)):
    email_list = session.query(EmailList.email).all()
    return {"emails": [email[0] for email in email_list]}

@app.post('/token', response_model=Token)
async def login_for_access_token(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES")))
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=UserPublic)
async def read_users_me(session: SessionDep, current_user: User = Depends(get_current_user)):
    return current_user