from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc
from datetime import datetime, timedelta
import os

from database import Session, NotificationHistory, User
from config import WEB_PORT

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory="widget"), name="static")

@app.get("/")
async def widget_page(token: str = Query(...)):
    """Главная страница виджета"""
    # Проверяем токен
    session = Session()
    user = session.query(User).filter_by(widget_token=token).first()
    session.close()
    
    if not user:
        return HTMLResponse("<h1>❌ Неверный токен виджета</h1>")
    
    # Возвращаем HTML виджета
    with open("widget/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(html)

@app.get("/api/widget")
async def get_widget_data(token: str = Query(...)):
    """API для получения данных виджета"""
    # Проверяем токен
    session = Session()
    user = session.query(User).filter_by(widget_token=token).first()
    session.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="Неверный токен")
    
    # Получаем последние уведомления
    session = Session()
    notifications = session.query(NotificationHistory)\
        .filter_by(user_id=user.telegram_id)\
        .order_by(desc(NotificationHistory.sent_at))\
        .limit(20)\
        .all()
    session.close()
    
    # Форматируем ответ
    result = []
    for notif in notifications:
        result.append({
            'type': notif.notification_type,
            'content': notif.content[:500],  # Ограничиваем длину
            'timestamp': notif.sent_at.isoformat()
        })
    
    return JSONResponse({
        'success': True,
        'notifications': result,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.get("/api/health")
async def health_check():
    """Проверка работоспособности"""
    return JSONResponse({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat()
    })

def run_web_server():
    """Запуск веб-сервера"""
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv('WEB_PORT', 8000)),
        log_level="info"
    )