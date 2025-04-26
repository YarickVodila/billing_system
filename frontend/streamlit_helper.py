import os
import requests
import streamlit as st

# FastAPI backend URL
BASE_URL = os.getenv("BACKEND_FASTAPI", "http://localhost:8000")

# Helper functions for API calls
def register_user(username, email, password):
    url = f"{BASE_URL}/register"
    data = {
        "username": username,
        "email": email,
        "password": password,
        # "balance": balance
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return True, response.json()["message"]
        else:
            return False, response.json().get("detail", "Registration failed")
    except Exception as e:
        return False, f"Error: {str(e)}"

def login_user(username, password):
    url = f"{BASE_URL}/login"
    try:
        # response = requests.post(url, data={"username": username, "password": password})
        response = requests.post(
            url, 
            json={"username": username, "password": password}
        )

        if response.status_code == 200:
            st.session_state.access_token = response.json()["access_token"]
            return True, "Login successful"
        else:
            return False, response.json().get("detail", "Login failed")
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_current_user():
    url = f"{BASE_URL}/user"
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            st.session_state.current_user = response.json()
            return True, response.json()
        else:
            return False, response.json().get("detail", "Failed to get user info")
    except Exception as e:
        return False, f"Error: {str(e)}"
    
def get_model_desc():
    url = f"{BASE_URL}/get_model_desc"
    # headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True, response.json()["data"]
        else:
            return False, response.json().get("detail", "Failed to get statistics")
    except Exception as e:
        return False, f"Error: {str(e)}"


def replenish_balance(amount):
    url = f"{BASE_URL}/balance_replenish"
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.post(url, headers=headers, params={"amount": amount})
        if response.status_code == 200:
            return True, response.json()["message"]
        else:
            return False, response.json().get("detail", "Balance replenish failed")
    except Exception as e:
        return False, f"Error: {str(e)}"

def make_prediction(model_id, data):
    url = f"{BASE_URL}/predict"
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.post(url, headers=headers, params={"model_id": model_id}, json=data)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get("detail", "Prediction failed")
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_statistics():
    url = f"{BASE_URL}/get_statistic"
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return True, response.json()["data"]
        else:
            return False, response.json().get("detail", "Failed to get statistics")
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_transaction_history(trans_type):
    url = f"{BASE_URL}/get_history_transaction"
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.get(url, headers=headers, params={"type_trans": trans_type})
        if response.status_code == 200:
            return True, response.json()["data"]
        else:
            return False, response.json().get("detail", "Failed to get transaction history")
    except Exception as e:
        return False, f"Error: {str(e)}"