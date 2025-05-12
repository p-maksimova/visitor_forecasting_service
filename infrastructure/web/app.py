import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests

def get_appointments(date, doctor_name):
    day = date.day
    month = date.month
    year = date.year
    url = f"http://fastapi_server:8000/get_appointments/{day}/{month}/{year}"
    
    # Параметры запроса, если нужны
    if doctor_name == "Все сотрудники":
        doctor_name = None
    params = {"doctor_name": doctor_name}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()   # Если статус-код не 200, выбросит исключение
        data = response.json()        # Преобразуем JSON данные в словарь
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP-ошибка: {http_err}")
    except Exception as err:
        print(f"Ошибка запроса: {err}")
     
def get_predict(date, doctor_name):
    day = date.day
    month = date.month
    year = date.year
    url = f"http://fastapi_server:8000/predict/{day}/{month}/{year}/{doctor_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()   # Если статус-код не 200, выбросит исключение
        data = response.json()        # Преобразуем JSON данные в словарь
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP-ошибка: {http_err}")
    except Exception as err:
        print(f"Ошибка запроса: {err}")

def main():
    st.title("Информационная система прогнозирования посещений")

    # Виджет для выбора даты
    selected_date = st.date_input("Выберите дату", value=datetime.date(2025, 4, 29))

    # Элемент с выбором из выпадающего списка
    options = ["Все сотрудники", "Иванов А.В.", "Смирнов О.П.", "Петров И.М.", "Соколов Д.Н.", "Васильев Е.С."]
    selected_option = st.selectbox("Выберите врача", options=options)

    col_left, col_right = st.columns([3, 1])
    with col_left:
        if st.button("Загрузить записи"):    
            appointments = get_appointments(selected_date, selected_option)
            df = pd.DataFrame(appointments)

    with col_right:
        if st.button("Получить прогноз"):    
            predict = get_predict(selected_date, selected_option)
            df = pd.DataFrame(predict)

    # Выводим таблицу
    try:
        st.table(df)
    except Exception:
        st.write("Данные отсутствуют")

if __name__ == "__main__":
    main()

