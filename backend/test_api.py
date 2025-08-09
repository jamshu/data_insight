import requests

# Test if backend is running
try:
    # Test root
    response = requests.get("http://localhost:8000/")
    print(f"Root endpoint: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test sessions endpoint
    response = requests.get("http://localhost:8000/api/sessions")
    print(f"\nSessions endpoint: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    
    # Test API docs
    response = requests.get("http://localhost:8000/docs")
    print(f"\nDocs endpoint: {response.status_code}")
    
except Exception as e:
    print(f"Error: {e}")
