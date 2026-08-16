from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc
from datetime import datetime
import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Session, NotificationHistory, User
from config import WEB_PORT

app = FastAPI(title="Warframe Bot Widget API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Проверяем существование папки widget
widget_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "widget")
if os.path.exists(widget_dir):
    app.mount("/static", StaticFiles(directory=widget_dir), name="static")

@app.get("/")
async def widget_page(token: str = Query(...)):
    """Главная страница виджета"""
    session = Session()
    user = session.query(User).filter_by(widget_token=token).first()
    session.close()
    
    if not user:
        return HTMLResponse("<h1>❌ Неверный токен виджета</h1>")
    
    widget_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "widget", "index.html")
    try:
        with open(widget_path, "r", encoding="utf-8") as f:
            html = f.read()
        return HTMLResponse(html)
    except FileNotFoundError:
        return HTMLResponse("<h1>❌ Виджет не найден</h1>")

@app.get("/api/widget")
async def get_widget_data(token: str = Query(...)):
    """API для получения данных виджета"""
    session = Session()
    user = session.query(User).filter_by(widget_token=token).first()
    session.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="Неверный токен")
    
    session = Session()
    notifications = session.query(NotificationHistory)\
        .filter_by(user_id=user.telegram_id)\
        .order_by(desc(NotificationHistory.sent_at))\
        .limit(20)\
        .all()
    session.close()
    
    result = []
    for notif in notifications:
        result.append({
            'type': notif.notification_type,
            'content': notif.content[:500],
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
    port = int(os.getenv('WEB_PORT', 8000))
    uvicorn.run(
        "web.server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    run_web_server()