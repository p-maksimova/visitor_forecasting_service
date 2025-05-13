import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler, StandardScaler
import category_encoders as ce
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
import os

def data_to_model(data) -> pd.DataFrame:
    data = pd.DataFrame(data)
    
    cols_to_int = ['scholarship', 'hipertension','diabetes', 'alcoholism', 'handcap', 'sms_received']
    data[cols_to_int] = data[cols_to_int].astype(int)
  
    mapping = {
        'gender': 'Gender',
        'age': 'Age',
        'neighbourhood': 'Neighbourhood',
        'scholarship': 'Scholarship',
        'hipertension': 'Hipertension',
        'diabetes': 'Diabetes',
        'alcoholism': 'Alcoholism',
        'handcap': 'Handcap',
        'sms_received': 'SMS_received',
        'appointment_cumcount': 'Appointment_cumcount'
    }
    data.rename(columns=mapping, inplace=True)

    data['appointment_date'] = pd.to_datetime(data['appointment_date'])
    data['scheduled_date'] = pd.to_datetime(data['scheduled_date'])
    data['day_diff'] = (data['appointment_date'] - data['scheduled_date']).dt.days
    data['Scheduled_dow'] = data['scheduled_date'].dt.weekday
    data['Scheduled_day'] = data['scheduled_date'].dt.day
    data['Scheduled_month'] = data['scheduled_date'].dt.month
    data['AppointmentDay_dow'] = data['appointment_date'].dt.weekday
    data['AppointmentDay_day'] = data['appointment_date'].dt.day

    return data

def predict_model(data, model):

    # Загружаем предварительно обученную ML модель.
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), model)

    try:
        with open(model_path, "rb") as f:
            ml_model = pickle.load(f)
    except Exception as e:
        raise Exception(f"Не удалось загрузить ML модель: {e}")

    answers = ["Прием", "Пропуск"]

    data = data_to_model(data)

    colums_predict = ['Gender', 'Age', 'Neighbourhood', 'Scholarship', 'Hipertension', 'Diabetes', 'Alcoholism', 'Handcap', 'SMS_received', 
                      'day_diff', 'Scheduled_dow', 'Scheduled_day', 'Scheduled_month', 'AppointmentDay_dow', 'AppointmentDay_day',
                      'Appointment_cumcount', 'no_show_ratio',  'no_show_cumsum']

    predict_proba = ml_model.predict_proba(data[colums_predict])
    data['probability_visit'] = predict_proba[:, 0]
    data['predict_visit'] = [answers[i] for i in ml_model.predict(data[colums_predict])] 

    colums_result = ["doctor_name", "slot_id", "patient_id", "appointment_id", "appointment_date", "scheduled_date", 
                     "probability_visit", "predict_visit"]
    
    result = data[colums_result].to_dict(orient="records")

    for record in result:
        for key, value in record.items():
            if isinstance(value, np.integer):
                record[key] = int(value)
            elif isinstance(value, np.floating):
                record[key] = float(value)

    return result