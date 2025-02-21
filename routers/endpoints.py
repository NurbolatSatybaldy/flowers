from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from auth import create_access_token, verify_token
from repositories import UsersRepository, FlowersRepository, PurchasesRepository
from passlib.hash import bcrypt
from fastapi.templating import Jinja2Templates
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
users_repo = UsersRepository()
flowers_repo = FlowersRepository()
purchases_repo = PurchasesRepository()
templates = Jinja2Templates(directory="templates")

@router.get("/signup", response_class=HTMLResponse)
def get_signup_form(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})

@router.post("/signup")
async def signup(email: str = Form(...), full_name: str = Form(...), password: str = Form(...), photo: UploadFile = File(None), database: Session = Depends(get_db)):
    hashed = bcrypt.hash(password)
    photo_url = None
    if photo:
        contents = await photo.read()
        import base64
        photo_url = "data:" + photo.content_type + ";base64," + base64.b64encode(contents).decode()
    user_id = users_repo.create_user(database, email, full_name, hashed, photo_url)
    return JSONResponse(status_code=200, content={"user_id": user_id})

@router.get("/login", response_class=HTMLResponse)
def get_login_form(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
def login(email: str = Form(...), password: str = Form(...), database: Session = Depends(get_db)):
    user = users_repo.get_user_by_email(database, email)
    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    response = RedirectResponse(url="/profile", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return response

@router.get("/profile", response_class=HTMLResponse)
def profile(request: Request, database: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = users_repo.get_user_by_id(database, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("auth/profile.html", {"request": request, "user": user})

@router.get("/flowers", response_class=HTMLResponse)
def get_flowers(request: Request, database: Session = Depends(get_db)):
    flowers = flowers_repo.get_all_flowers(database)
    return templates.TemplateResponse("flowers/list.html", {"request": request, "flowers": flowers})

@router.post("/flowers")
def add_flower(name: str = Form(...), quantity: int = Form(...), price: float = Form(...), database: Session = Depends(get_db)):
    flower_id = flowers_repo.create_flower(database, name, quantity, price)
    return JSONResponse(status_code=200, content={"flower_id": flower_id})

@router.patch("/flowers/{flower_id}")
def update_flower(flower_id: int, name: str = Form(None), quantity: int = Form(None), price: float = Form(None), database: Session = Depends(get_db)):
    flower = flowers_repo.update_flower(database, flower_id, name, quantity, price)
    if not flower:
        raise HTTPException(status_code=404, detail="Flower not found")
    return JSONResponse(status_code=200, content={"flower": {"id": flower.id, "name": flower.name, "quantity": flower.quantity, "price": float(flower.price)}})

@router.delete("/flowers/{flower_id}")
def delete_flower(flower_id: int, database: Session = Depends(get_db)):
    flower_id_deleted = flowers_repo.delete_flower(database, flower_id)
    if not flower_id_deleted:
        raise HTTPException(status_code=404, detail="Flower not found")
    return JSONResponse(status_code=200, content={"deleted_flower_id": flower_id_deleted})

@router.post("/cart/items")
def add_to_cart(request: Request, flower_id: int = Form(...)):
    cart = request.cookies.get("cart")
    items = cart.split(",") if cart else []
    items.append(str(flower_id))
    response = JSONResponse(status_code=200, content={"message": "Flower added to cart"})
    response.set_cookie(key="cart", value=",".join(items), httponly=True)
    return response

@router.get("/cart/items", response_class=HTMLResponse)
def get_cart(request: Request, database: Session = Depends(get_db)):
    cart = request.cookies.get("cart")
    if not cart:
        return templates.TemplateResponse("cart/list.html", {"request": request, "items": [], "total": 0})
    flower_ids = [int(fid) for fid in cart.split(",")]
    items = []
    total = 0
    for fid in flower_ids:
        f = flowers_repo.get_flower_by_id(database, fid)
        if f:
            items.append({"id": f.id, "name": f.name, "price": float(f.price)})
            total += float(f.price)
    return templates.TemplateResponse("cart/list.html", {"request": request, "items": items, "total": total})

@router.post("/purchased")
def purchase(request: Request, database: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    cart = request.cookies.get("cart")
    if not cart:
        return JSONResponse(status_code=200, content={"message": "Cart is empty"})
    flower_ids = [int(fid) for fid in cart.split(",")]
    for fid in flower_ids:
        purchases_repo.add_purchase(database, int(user_id), fid)
    response = JSONResponse(status_code=200, content={"message": "Purchase successful"})
    response.delete_cookie("cart")
    return response

@router.get("/purchased", response_class=HTMLResponse)
def get_purchased(request: Request, database: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    purchases = purchases_repo.get_purchases_by_user(database, int(user_id))
    return templates.TemplateResponse("flowers/purchased.html", {"request": request, "purchases": purchases})
