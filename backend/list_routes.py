from main import app

for route in app.routes:
    if hasattr(route, 'path'):
        print(f"{route.path} - {route.methods if hasattr(route, 'methods') else 'N/A'}")
