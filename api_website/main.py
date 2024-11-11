from fastapi import FastAPI, Depends, status, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from auth import create_access_token, is_user_auth
from database import User, get_chats_by_user
from database import verify_password, get_password_hash, engine, Base, get_db, create_chat, delete_chat, \
    search_chats_by_name
from orm import ChatCreate, ChatTokenRequest

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secret_key_123")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="templates/static"), name="static")

# Обработчик для страницы регистрации
@app.get("/register", response_class=HTMLResponse)
def show_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Обработчик для страницы логина
@app.get("/login", response_class=HTMLResponse)
def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# User registration route
@app.post("/register/", response_class=HTMLResponse)
async def register(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...)
):
    # Проверка существующего пользователя
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email уже зарегистрирован"})

    # Хэширование пароля и создание пользователя
    hashed_password = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return response

# User login route
@app.post("/login/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    user = db.query(User).filter(User.email == username).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неправильный email или пароль"})

    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    request.session["user"] = {"email": user.email, "id": user.id}
    request.session["token"] = access_token
    return response

@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return response

# Обработчик для корневой страницы
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db), is_auth: bool = Depends(is_user_auth)):
    user = request.session.get("user")
    if is_auth:
        user_chats = get_chats_by_user(db, user['id'])  # Получаем список чатов пользователя
        return templates.TemplateResponse("index.html", {"request": request, "user_chats": user_chats, "user": user})
    return templates.TemplateResponse("index.html", {"request": request, "user": None})

# Обработчик создания чата
@app.post("/create-chat")
async def create_chat_endpoint(request: Request, db: Session = Depends(get_db), room_name: str = Form(...)):
    user = request.session.get("user")
    if user:
        chat_data = ChatCreate(name=room_name)
        create_chat(db, chat_data, user["id"])
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return {"error": "User not authenticated"}

# Обработчик удаления чата
@app.delete("/delete-chat/{id}")
async def delete_chat_endpoint(request: Request, id: int, db: Session = Depends(get_db)):
    user = request.session.get("user")
    if user:
        delete_chat(db, id, user["id"])
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return {"error": "User not authenticated"}

# Обработчик поиска чатов
@app.get("/search-chats", response_class=JSONResponse)
async def search_chats(request: Request, query: str = Query(...), db: Session = Depends(get_db)):
    user = request.session.get("user")
    if user:
        found_chats = search_chats_by_name(db, query)
        chat_list = [{"name": chat.name} for chat in found_chats]
        return JSONResponse(content={"chats": chat_list})
    return JSONResponse(content={"error": "User not authenticated"}, status_code=401)

@app.post("/get_token_chat/")
async def get_token_for_chat(chat_request: ChatTokenRequest, request: Request):
    user = request.session.get("user")

    if not chat_request.chat_name:
        raise HTTPException(status_code=400, detail="Chat name is required")

    access_token = create_access_token(data={"sub": user["email"], "name_chat": chat_request.chat_name})

    return {"access_token": access_token, "token_type": "bearer"}

