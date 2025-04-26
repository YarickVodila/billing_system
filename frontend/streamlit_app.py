from streamlit_helper import register_user, login_user, get_current_user, replenish_balance, make_prediction, get_statistics, get_transaction_history, get_model_desc
import os
import streamlit as st
from datetime import datetime
import pandas as pd


# Initialize session state
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Streamlit UI
st.set_page_config(page_title="Credit Prediction App", layout="wide")

# Main app
def main():
    st.title("Credit Prediction Application")
    st.markdown("""
    Это приложение взаимодействует с серверной частью FastAPI для:
    - регистрации и аутентификации пользователей
    - составления кредитных прогнозов с использованием различных моделей машинного обучения
    - просмотра истории прогнозов и транзакций
    """)

    # Navigation
    menu = ["Home", "Login", "Register", "Личный кабинет", "Make Prediction", "History"]
    if st.session_state.access_token:
        menu.remove("Login")
        menu.remove("Register")
    else:
        menu.remove("Личный кабинет")
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
        st.subheader("Регистрация нового пользователя")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        # balance = st.number_input("Initial Balance", min_value=0, value=1000)
        
        if st.button("Зарегистрироваться"):
            if username and email and password:
                success, message = register_user(username, email, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Пожалуйста заполните все поля")

    elif choice == "Личный кабинет":
        st.subheader("Личный кабинет")
        if st.session_state.current_user:
            user = st.session_state.current_user
            st.write(f"### Добро пожаловать, {user['username']}!")
            st.write(f"#### Ваш баланс в мёртвых президентах: ${user['balance']}")
            
            # Balance replenishment
            st.write("### Пополнить баланс на халяву")
            amount = st.number_input("Количество мёртвых президентов", min_value=1, value=100)
            if st.button("Пополнить"):
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
            st.write(f"Ваш баланс в мёртвых президентах: ${user['balance']}")
            
            success, models_data = get_model_desc()

            # Model selection
            model_id = st.radio("Выберите модель", 
                                options=[str(model["id"]) for model in models_data],
                                format_func=lambda x: {str(model["id"]): f'{model["name"]} (Coast: ${model["cost"]})'  for model in models_data}[x],
                                captions = [f'{model["description"]}' for model in models_data]
            )                   
            
            # Input form
            st.write("### Заполните форму")
            with st.form("prediction_form"):
                col1, col2 = st.columns(2)
                
                loan_intent_hash = {
                    "Предпринимательство": 'VENTURE', 
                    "Медицина": 'MEDICAL', 
                    "Образование": 'EDUCATION', 
                    "Закрытие долгов": 'DEBTCONSOLIDATION', 
                    "Личное": 'PERSONAL', 
                    "Ремонт дома": 'HOMEIMPROVEMENT'
                }

                cb_person_default_on_file_hash = {
                    "Да": "Y",
                    "Нет": "N"
                }

                with col1:
                    person_age = st.number_input("Возраст", min_value=0, value=30)
                    person_income = st.number_input("Заработная плата в год ($)", min_value=0, value=50000)
                    person_emp_length = st.number_input("Опыт работы (кол-во лет)", min_value=0, value=5)
                    loan_intent = st.selectbox("На что нужен кредит", ['Предпринимательство', 'Медицина', 'Образование', 'Закрытие долгов', 'Личное', 'Ремонт дома'])
                    loan_grade = st.selectbox("Кредитный рейтинг", ['A', 'C', 'B', 'D', 'E', 'F', 'G'])
                
                with col2:
                    loan_amnt = st.number_input("Сумма кредита ($)", min_value=0, value=10000)
                    loan_int_rate = st.number_input("Процентная ставка (%)", min_value=0.0, value=5.0)
                    loan_percent_income = st.number_input("Процент от дохода на погашение кредита", min_value=0.0,  value=0.2)
                    cb_person_default_on_file = st.selectbox("Были ли просрочки по кредитам", ["Да", "Нет"])
                    cb_person_cred_hist_length = st.number_input("Кредитная история (кол-во лет)", min_value=0, value=3)
                
                submitted = st.form_submit_button("Make Prediction")
                
                if submitted:
                    
                    loan_intent = loan_intent_hash[loan_intent]
                    cb_person_default_on_file = cb_person_default_on_file_hash[cb_person_default_on_file]

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