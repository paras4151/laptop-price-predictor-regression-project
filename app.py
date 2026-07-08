import streamlit as st
import pickle
import numpy as np
import pandas as pd

# import the model
pipe = pickle.load(open('pipe.pkl', 'rb'))
df = pickle.load(open('df.pkl', 'rb'))

st.title("Laptop Predictor")

# brand
company = st.selectbox('Brand', df['Company'].unique())

# type of laptop
type = st.selectbox('Type', df['TypeName'].unique())

# Ram
ram = st.selectbox('RAM(in GB)', [2, 4, 6, 8, 12, 16, 24, 32, 64])

# weight
weight = st.number_input('Weight of the Laptop', min_value=0.1, value=1.5)

# Touchscreen
touchscreen = st.selectbox('Touchscreen', ['No', 'Yes'])

# IPS
ips = st.selectbox('IPS', ['No', 'Yes'])

# screen size
screen_size = st.number_input('Screen Size', min_value=1.0, value=13.0)

# resolution
resolution = st.selectbox('Screen Resolution',
                           ['1920x1080', '1366x768', '1600x900', '3840x2160', '3200x1800',
                            '2880x1800', '2560x1600', '2560x1440', '2304x1440'])

# cpu
cpu = st.selectbox('CPU', df['Cpu brand'].unique())

hdd = st.selectbox('HDD(in GB)', [0, 128, 256, 512, 1024, 2048])

ssd = st.selectbox('SSD(in GB)', [0, 8, 128, 256, 512, 1024])

gpu = st.selectbox('GPU', df['Gpu brand'].unique())

os = st.selectbox('OS', df['os'].unique())

if st.button('Predict Price'):
    # query
    touchscreen_val = 1 if touchscreen == 'Yes' else 0
    ips_val = 1 if ips == 'Yes' else 0

    X_res = int(resolution.split('x')[0])
    Y_res = int(resolution.split('x')[1])
    ppi = ((X_res ** 2) + (Y_res ** 2)) ** 0.5 / screen_size

    # Build a single-row DataFrame with the exact column names/dtypes the
    # pipeline was trained on. Passing a plain numpy array here silently
    # casts every value (including the numeric ones) to strings, which is
    # what caused prediction to fail before.
    query = pd.DataFrame([{
        'Company': company,
        'TypeName': type,
        'Ram': int(ram),
        'Weight': float(weight),
        'Touchscreen': touchscreen_val,
        'Ips': ips_val,
        'ppi': ppi,
        'Cpu brand': cpu,
        'HDD': int(hdd),
        'SSD': int(ssd),
        'Gpu brand': gpu,
        'os': os,
    }])

    predicted_price = int(np.exp(pipe.predict(query)[0]))
    st.title("The predicted price of this configuration is " + str(predicted_price))
