from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
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

# Путь к папке с виджетом
WIDGET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "widget")

# Монтируем статические файлы
if os.path.exists(WIDGET_DIR):
    app.mount("/static", StaticFiles(directory=WIDGET_DIR), name="static")

@app.get("/")
async def widget_page(token: str = Query(None)):
    """Главная страница виджета"""
    
    # Если токен не передан, показываем страницу с инструкцией
    if not token:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Warframe Widget</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: #1a1a2e;
                    color: white;
                    text-align: center;
                }
                .container {
                    padding: 40px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 16px;
                    max-width: 400px;
                }
                .container h1 { color: #ff6b6b; }
                .container p { color: #aaa; }
                .container a {
                    color: #4ecdc4;
                    text-decoration: none;
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: rgba(78, 205, 196, 0.2);
                    border-radius: 8px;
                    border: 1px solid #4ecdc4;
                }
                .container a:hover {
                    background: rgba(78, 205, 196, 0.3);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📱 Warframe Widget</h1>
                <p>Для использования виджета, пожалуйста, получите токен через бота командой <strong>/widget</strong></p>
                <a href="https://t.me/Pocketcephalonbot">📲 Открыть бота</a>
            </div>
        </body>
        </html>
        """)
    
    # Проверяем токен
    session = Session()
    user = session.query(User).filter_by(widget_token=token).first()
    session.close()
    
    if not user:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ошибка виджета</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: #1a1a2e;
                    color: white;
                    text-align: center;
                }
                .error {
                    padding: 40px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 16px;
                    max-width: 400px;
                }
                .error h1 { color: #ff6b6b; }
                .error p { color: #aaa; }
                .error a {
                    color: #4ecdc4;
                    text-decoration: none;
                    display: inline-block;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="error">
                <h1>❌ Неверный токен виджета</h1>
                <p>Пожалуйста, получите новый токен через бота командой /widget</p>
                <a href="https://t.me/Pocketcephalonbot">📱 Открыть бота</a>
            </div>
        </body>
        </html>
        """)
    
    # Отдаем HTML виджета
    widget_path = os.path.join(WIDGET_DIR, "index.html")
    if not os.path.exists(widget_path):
        return HTMLResponse("<h1>❌ Файл виджета не найден</h1>")
    
    with open(widget_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    return HTMLResponse(html)

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
            'content': notif.content[:500] if notif.content else "Нет содержимого",
            'timestamp': notif.sent_at.isoformat() if notif.sent_at else datetime.utcnow().isoformat()
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
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    })

@app.get("/favicon.ico")
async def favicon():
    """Возвращает пустую иконку"""
    return JSONResponse({}, status_code=204)

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
