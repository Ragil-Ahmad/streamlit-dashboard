import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def create_season_weather_group(day_clean_data):
    season_weather_group = day_clean_data.groupby(['season', 'weather_condition'])['count'].mean().reset_index()
    season_weather_group['season'] = pd.Categorical(season_weather_group['season'], categories=['Spring', 'Summer', 'Fall', 'Winter'], ordered=True)
    return season_weather_group

def create_weekday_avg(day_clean_data):
    weekday_avg = day_clean_data.groupby('weekday')[['registered', 'casual']].mean().mean()
    return weekday_avg

def create_workingday_avg(day_clean_data):
    workingday_avg = day_clean_data.groupby('workingday')[['registered', 'casual']].mean().mean()
    return workingday_avg

def create_holiday_avg(day_clean_data):
    holiday_avg = day_clean_data.groupby('holiday')[['registered', 'casual']].mean().mean()
    return holiday_avg

def create_hourly_registered(hour_clean_data):
    hourly_registered = hour_clean_data.groupby('hour')['registered'].mean()
    return hourly_registered

def create_hourly_casual(hour_clean_data):
    hourly_casual = hour_clean_data.groupby('hour')['casual'].mean()
    return hourly_casual

def create_casual_user(day_clean_data):
    casual_user = day_clean_data.groupby(by='date').agg({
        'casual': 'sum'
    }).reset_index()
    return casual_user

def create_registered_user(day_clean_data):
    registered_user = day_clean_data.groupby(by='date').agg({
        'registered': 'sum'
    }).reset_index()
    return registered_user

def create_daily_user_count(day_clean_data):
    daily_user_count = day_clean_data.groupby(by='date').agg({
        'count': 'sum'
    }).reset_index()
    return daily_user_count
# Read Data
day_df = pd.read_csv('day_clean_data.csv')
hour_df = pd.read_csv('hour_clean_data.csv')

# Sort and preprocess
datetime_columns = ["date"]
day_df.sort_values(by="date", inplace=True)
day_df.reset_index(inplace=True)

hour_df.sort_values(by="date", inplace=True)
hour_df.reset_index(inplace=True)

# Convert date columns to datetime
for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])
    hour_df[column] = pd.to_datetime(hour_df[column])

# Sidebar for Date Input
min_date_days = day_df["date"].min()
max_date_days = day_df["date"].max()

min_date_hour = hour_df["date"].min()
max_date_hour = hour_df["date"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://camo.githubusercontent.com/e7e99e60ef795eb3ae37545e6a1f84391d462097d74c69d378daaab5660ed444/687474703a2f2f6369747962696b2e65732f66696c65732f707962696b65732e706e67")

    # Get date range for filtering data
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])

main_df_day = day_df[(day_df["date"] >= str(start_date)) & (day_df["date"] <= str(end_date))]
main_df_hour = hour_df[(hour_df["date"] >= str(start_date)) & (hour_df["date"] <= str(end_date))]

# Create groupings
season_weather_group = create_season_weather_group(main_df_day)
weekday_avg = create_weekday_avg(main_df_day)
workingday_avg = create_workingday_avg(main_df_day)
holiday_avg = create_holiday_avg(main_df_day)
hourly_registered = create_hourly_registered(main_df_hour)
hourly_casual = create_hourly_casual(main_df_hour)
daily_casual = create_casual_user(main_df_day)
daily_registered = create_registered_user(main_df_day)
daily_user = create_daily_user_count(main_df_day)
# Streamlit App Header
st.header('Penyewaan Sepeda :sparkles:')

col1, col2, col3 = st.columns(3)

with col1:
    daily_rent_casual = daily_casual['casual'].sum()
    st.metric('Casual User', value= daily_rent_casual)

with col2:
    daily_rent_registered = daily_registered['registered'].sum()
    st.metric('Registered User', value= daily_rent_registered)

with col3:
    daily_rent_user = daily_user['count'].sum()
    st.metric('Total Daily User', value=daily_rent_user)
# Pivot Table for Season & Weather Group
pivot_table = season_weather_group.pivot(index='season', columns='weather_condition', values='count')

# Streamlit - Display Chart for Season & Weather Group
st.subheader('Aktivitas Penyewaan Sepeda Berdasarkan Musim dan Kondisi Cuaca Setiap Hari')

fig, ax = plt.subplots(figsize=(12, 6))
pivot_table.plot(kind='bar', ax=ax)
ax.set_ylabel('Rata-rata Penyewaan')
ax.set_xlabel('Musim')
ax.set_xticklabels(pivot_table.index, rotation=0)
ax.legend(title='Kondisi Cuaca', bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Call tight_layout on the figure object
fig.tight_layout()

# Display the first plot in Streamlit
st.pyplot(fig)

# Monthly Sales Trend
st.subheader("Pada Jam Berapa Penyewaan Sepeda Mencapai 'Peak' nya")

# Create Line Chart for Hourly Registered & Casual Users
fig2, ax2 = plt.subplots(figsize=(12, 6))
ax2.plot(hourly_registered.index, hourly_registered, label='Registered', marker='o', color='blue')
ax2.plot(hourly_casual.index, hourly_casual, label='Casual', marker='o', color='orange')

# Add Titles, Labels, and Legend
ax2.set_title('Perbandingan Pola Penggunaan Sepeda Berdasarkan Waktu (Jam)')
ax2.set_xlabel('Jam')
ax2.set_ylabel('Rata-rata Penyewaan')
ax2.legend(title='Tipe Pengguna')
ax2.grid(axis='both', linestyle='--', alpha=0.7)  # Add grid for better readability
ax2.set_xticks(range(0, 24))  # Ensure all hours (0-23) are visible

# Call tight_layout on the figure object
fig2.tight_layout()

# Display the second plot in Streamlit
st.pyplot(fig2)

st.subheader("Bagaimana tren penyewaan sepeda pada saat hari biasa, liburan atau hari kerja")

# Data untuk plotting
categories = ['Weekday', 'Workday', 'Holiday']
registered_avg = [weekday_avg['registered'], workingday_avg['registered'], holiday_avg['registered']]
casual_avg = [weekday_avg['casual'], workingday_avg['casual'], holiday_avg['casual']]

x = np.arange(len(categories))  # Posisi untuk kategori
width = 0.35  # Lebar bar

# Membuat bar chart dengan Matplotlib
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(x - width/2, registered_avg, width, label='Registered', color='blue', alpha=0.7)
ax.bar(x + width/2, casual_avg, width, label='Casual', color='orange', alpha=0.7)

# Menambahkan label dan legend
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.set_xlabel('Kategori')
ax.set_ylabel('Rata-rata Penyewaan')
ax.set_title('Pola Penggunaan Sepeda Berdasarkan Weekday, Workday, dan Holiday')
ax.legend(title='Tipe Pengguna')
ax.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Menampilkan grafik di Streamlit
st.pyplot(fig)