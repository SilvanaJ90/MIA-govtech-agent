import requests

API_BASE = "http://127.0.0.1:5000"  # Ajusta al host de tu backend Flask

def api_login(email, password):
    res = requests.post(f"{API_BASE}/login", json={"email": email, "password": password})
    return res.json(), res.status_code

def api_register(email, password, first_name, last_name, role="user"):
    res = requests.post(f"{API_BASE}/register", json={
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "role": role
    })
    return res.json(), res.status_code
