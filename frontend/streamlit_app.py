import os
import streamlit as st
import requests
from datetime import datetime
import pandas as pd


# FastAPI backend URL
BASE_URL = os.getenv("BACKEND_FASTAPI", "http://localhost:8000") # "http://localhost:8000"  # Change this if your backend is hosted elsewhere

# Initialize session state
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

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

# Streamlit UI
st.set_page_config(page_title="Credit Prediction App", layout="wide")

# Main app
def main():
    st.title("Credit Prediction Application")
    st.markdown("""
    This application interacts with a FastAPI backend to:
    - Register and authenticate users
    - Make credit predictions using different ML models
    - View prediction history and transactions
    """)

    # Navigation
    menu = ["Home", "Login", "Register", "Dashboard", "Make Prediction", "History"]
    if st.session_state.access_token:
        menu.remove("Login")
        menu.remove("Register")
    else:
        menu.remove("Dashboard")
        menu.remove("Make Prediction")
        menu.remove("History")

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        st.write("Welcome to the Credit Prediction App!")
        st.write("Please login or register to continue.")

    elif choice == "Login":
        st.subheader("Login Section")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username and password:
                success, message = login_user(username, password)
                if success:
                    st.success(message)
                    # Get user info after successful login
                    get_current_user()
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter both username and password")

    elif choice == "Register":
        st.subheader("Register New User")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        # balance = st.number_input("Initial Balance", min_value=0, value=1000)
        
        if st.button("Register"):
            if username and email and password:
                success, message = register_user(username, email, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Please fill all fields")

    elif choice == "Dashboard":
        st.subheader("User Dashboard")
        if st.session_state.current_user:
            user = st.session_state.current_user
            st.write(f"### Welcome, {user['username']}!")
            st.write(f"#### Your current balance: ${user['balance']}")
            
            # Balance replenishment
            st.write("### Replenish Balance")
            amount = st.number_input("Amount to add", min_value=1, value=100)
            if st.button("Add Funds"):
                success, message = replenish_balance(amount)
                if success:
                    st.success(message)
                    # Refresh user info
                    get_current_user()
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.warning("Please login first")

    elif choice == "Make Prediction":
        st.subheader("Make a Prediction")
        if st.session_state.current_user:
            user = st.session_state.current_user
            st.write(f"Your current balance: ${user['balance']}")
            
            # Model selection
            model_id = st.radio("Select Model", 
                                options=["1", "2", "3"],
                                format_func=lambda x: {
                                    "1": "Linear Regression (Cost: $10)",
                                    "2": "Random Forest (Cost: $20)",
                                    "3": "CatBoost (Cost: $30)"
                                }[x])
            
            # Input form
            st.write("### Enter Prediction Data")
            with st.form("prediction_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    person_age = st.number_input("Age", min_value=18, max_value=100, value=30)
                    person_income = st.number_input("Annual Income ($)", min_value=0, value=50000)
                    person_emp_length = st.number_input("Employment Length (years)", min_value=0, value=5)
                    loan_intent = st.selectbox("Loan Intent", ["EDUCATION", "MEDICAL", "VENTURE", "PERSONAL", "DEBTCONSOLIDATION", "HOMEIMPROVEMENT"])
                    loan_grade = st.selectbox("Loan Grade", ["A", "B", "C", "D", "E", "F", "G"])
                
                with col2:
                    loan_amnt = st.number_input("Loan Amount ($)", min_value=0, value=10000)
                    loan_int_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=100.0, value=5.0)
                    loan_percent_income = st.number_input("Loan Percent of Income", min_value=0.0, max_value=1.0, value=0.2)
                    cb_person_default_on_file = st.selectbox("Previous Default", ["Y", "N"])
                    cb_person_cred_hist_length = st.number_input("Credit History Length (years)", min_value=0, value=3)
                
                submitted = st.form_submit_button("Make Prediction")
                
                if submitted:
                    data = {
                        "person_age": person_age,
                        "person_income": person_income,
                        "person_emp_length": person_emp_length,
                        "loan_intent": loan_intent,
                        "loan_grade": loan_grade,
                        "loan_amnt": loan_amnt,
                        "loan_int_rate": loan_int_rate,
                        "loan_percent_income": loan_percent_income,
                        "cb_person_default_on_file": cb_person_default_on_file,
                        "cb_person_cred_hist_length": cb_person_cred_hist_length
                    }
                    
                    success, result = make_prediction(model_id, data)
                    if success:
                        st.success(f"Prediction task submitted! Task ID: {result['task_id']}")
                        st.info("Your prediction will be processed shortly. Check the History section for results.")
                        # Refresh user info
                        get_current_user()
                        st.rerun()
                    else:
                        st.error(result)
        else:
            st.warning("Please login first")

    elif choice == "History":
        st.subheader("History")
        if st.session_state.current_user:
            tab1, tab2 = st.tabs(["Predictions", "Transactions"])
            
            with tab1:
                st.write("### Prediction History")
                success, data = get_statistics()
                if success:
                    if data:
                        df = pd.DataFrame(data)
                        # Convert timestamp to readable format
                        if 'timestamp' in df.columns:
                            df['timestamp'] = pd.to_datetime(df['timestamp']) # .dt.strftime('%Y-%m-%d %H:%M:%S')
                        
                        df["Model_name"] = None
                        df.loc[df["model_id"] == 1, "Model_name"] = "Linear Regression"
                        df.loc[df["model_id"] == 2, "Model_name"] = "Random Forest"
                        df.loc[df["model_id"] == 3, "Model_name"] = "CatBoost"
                        df = df.drop(columns=["model_id"])

                        st.dataframe(df)
                    else:
                        st.info("No prediction history found")
                else:
                    st.error(data)
            
            with tab2:
                st.write("### Transaction History")
                trans_type = st.radio("Transaction Type", ["пополнение", "покупка"], index=0)
                success, data = get_transaction_history(trans_type)
                if success:
                    if data:
                        df = pd.DataFrame(data)
                        # Convert timestamp to readable format
                        if 'timestamp' in df.columns:
                            df['timestamp'] = pd.to_datetime(df['timestamp']) # .dt.strftime('%Y-%m-%d %H:%M:%S')
                        st.dataframe(df)
                    else:
                        st.info(f"No {trans_type} transactions found")
                else:
                    st.error(data)
        else:
            st.warning("Please login first")

if __name__ == "__main__":
    main()