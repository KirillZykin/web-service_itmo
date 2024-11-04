from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import secrets

from database import SessionLocal, engine, Base, get_db
from schemas import UserCreate, Token, UserResponse
from utils import verify_password, get_password_hash
from auth import create_access_token, get_current_user
from database import User

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
# Генерация ключа для подписи cookies
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))
templates = Jinja2Templates(directory="templates")
# Настройка маршрута для статических файлов
app.mount("/static", StaticFiles(directory="templates/static"), name="static")

# Обработчик для корневой страницы
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
    
    # Создание JWT токена и установка его в cookie
    access_token = create_access_token(data={"sub": new_user.email})
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

# User login route
@app.post("/login/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    user = db.query(User).filter(User.email == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неправильный email или пароль"})
    
    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


# Protected route to check JWT token validity
@app.get("/me/", response_model=UserResponse)
def access_cabinet(current_user: User = Depends(get_current_user)):
    return {"message": f"Welcome to your cabinet, {current_user.email}!", "user": current_user}

# Обработчик для корневой страницы
@app.get("/")
async def home(request: Request):
    user = request.session.get("user")
    if user:
        user_chats = [1, 2, 3]  # Здесь вы можете получить реальные чаты пользователя из базы данных
        return templates.TemplateResponse("index.html", {"request": request, "user_chats": user_chats, "user": user})
    return templates.TemplateResponse("index.html", {"request": request, "user": None})

