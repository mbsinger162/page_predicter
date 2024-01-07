import streamlit as st
import pandas as pd
import joblib
from datetime import datetime

# # Custom CSS to increase label sizes and set font
# def local_css(file_name):
#     with open(file_name, "r") as f:
#         st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# # Use the function
# local_css("style.css")

# Load the model
model = joblib.load('gradient_boosting_best_model.pkl')

def predict_page_count(hour, temp_celsius, month, day_of_week):
    # Create a DataFrame with the input values
    input_data = pd.DataFrame({
        'hour': [hour],
        'temp': [temp_celsius],
        'month': [month],
        'day_of_week': [day_of_week]
    })

    # Make a prediction
    prediction = model.predict(input_data)
    return prediction[0]

def convert_to_24h(hour_str, period):
    hour = int(hour_str) if hour_str.isdigit() else 0
    if period == 'PM' and hour < 12:
        hour += 12
    elif period == 'AM' and hour == 12:
        hour = 0
    return hour

def get_hourly_predictions(start_day, end_day, start_hour, end_hour, temp_fahrenheit, month):
    total_pages = 0
    temp_celsius = (5/9) * (temp_fahrenheit - 32)

    # Calculate the number of days in the range, considering the wrap-around from Sunday to Monday
    day_range = (end_day - start_day + 7) % 7 + 1

    # Iterate over each day and hour in the interval
    for day_offset in range(day_range):
        current_day = (start_day + day_offset) % 7
        for hour in range(start_hour if day_offset == 0 else 0, end_hour + 1 if current_day == end_day else 24):
            total_pages += predict_page_count(hour, temp_celsius, month, current_day)

    return total_pages


# Streamlit interface
st.title('Yale Ophtho PGY2 Page Predictor')

# User inputs
temp_fahrenheit = st.number_input('Enter the temperature in Fahrenheit:', min_value=-100, max_value=130, value=60)
month = st.selectbox('Select the month:', range(1, 13), format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
start_day = st.selectbox('Select start day of the week:', range(7), format_func=lambda x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][x])

col1, col2 = st.columns(2)
with col1:
    start_hour = st.text_input('Enter start hour (1-12):', '1')
with col2:
    start_period = st.selectbox('Start AM/PM:', ['AM', 'PM'])

end_day = st.selectbox('Select end day of the week:', range(7), format_func=lambda x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][x])

col3, col4 = st.columns(2)
with col3:
    end_hour = st.text_input('Enter end hour (1-12):', '12')
with col4:
    end_period = st.selectbox('End AM/PM:', ['AM', 'PM'], index=1)

# Convert to 24-hour format
start_hour_24 = convert_to_24h(start_hour, start_period)
end_hour_24 = convert_to_24h(end_hour, end_period)

# Predict button
if st.button('Predict Page Count'):
    total_pages = get_hourly_predictions(start_day, end_day, start_hour_24, end_hour_24, temp_fahrenheit, month)
    st.write(f'Total predicted pages in the given interval: {total_pages}')

# Run this app with `streamlit run app.py`
