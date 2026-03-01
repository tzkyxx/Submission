import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi Halaman
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")
sns.set(style='whitegrid')

# --- HELPER FUNCTIONS ---
def create_hourly_rent_df(df):
    return df.groupby('hour').total_rentals.sum().reset_index()

def create_daily_rent_df(df):
    return df.groupby('weekday').total_rentals.sum().reset_index()

def create_season_rent_df(df):
    return df.groupby('season').total_rentals.sum().reset_index()

def create_weather_rent_df(df):
    return df.groupby('weathersit').total_rentals.sum().reset_index()

def create_user_type_df(df):
    user_type_sum = df[['casual_users', 'registered_users']].sum().reset_index()
    user_type_sum.columns = ['user_type', 'total_users']
    return user_type_sum

def create_hourly_user_df(df):
    return df.groupby('hour')[['casual_users', 'registered_users']].sum().reset_index()

def create_daily_user_df(df):
    daily_user_df = df.groupby('weekday')[['casual_users', 'registered_users']].sum().reset_index()
    return pd.melt(daily_user_df, id_vars='weekday')

# --- LOAD DATA ---
@st.cache_data
def load_data():
    day_df = pd.read_csv("dashboard/day.csv")
    hour_df = pd.read_csv("dashboard/hour.csv")
    day_df['date'] = pd.to_datetime(day_df['date'])
    hour_df['date'] = pd.to_datetime(hour_df['date'])
    return day_df, hour_df

day_df, hour_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
   
    st.image("dashboard/nice-ride.jpg")
    
    # Filter Rentang Waktu
    min_date = day_df["date"].min()
    max_date = day_df["date"].max()
    
    try:
        start_date, end_date = st.date_input(
            label='Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except ValueError:
        st.error("Pilih rentang waktu yang valid")
        st.stop()

# Filter dataframe berdasarkan input
main_day_df = day_df[(day_df["date"] >= str(start_date)) & (day_df["date"] <= str(end_date))]
main_hour_df = hour_df[(hour_df["date"] >= str(start_date)) & (hour_df["date"] <= str(end_date))]

# --- DASHBOARD HEADER ---
st.title('🚲 Bike Sharing Analytics Dashboard')
st.markdown(f"Menampilkan data dari **{start_date}** hingga **{end_date}**")

# Row 1: Metrik Utama
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Rentals", value=f"{main_day_df.total_rentals.sum():,}")
with col2:
    st.metric("Registered Users", value=f"{main_day_df.registered_users.sum():,}")
with col3:
    st.metric("Casual Users", value=f"{main_day_df.casual_users.sum():,}")

st.divider()

# --- VISUALISASI PERTANYAAN BISNIS ---

# Pertanyaan 1: Siklus Waktu (Jam & Hari)
st.subheader("1. Pola Penyewaan Berdasarkan Waktu")
col_a, col_b = st.columns(2)
col_c, col_d = st.columns(2)

with col_a:
    st.write("**Total Penyewaan Berdasarkan Jam**")
    hourly_df = create_hourly_rent_df(main_hour_df)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        data=hourly_df, 
        x='hour', 
        y='total_rentals', 
        marker='o', 
        color='blue', 
        ax=ax
    )
    ax.set_xticks(range(0, 24))
    ax.set_xlabel("Jam")
    ax.set_ylabel("Jumlah Sewa")
    st.pyplot(fig)

with col_b:
    st.write("**Total Penyewaan per Hari (Tahun ke Tahun)**")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        data=main_hour_df, 
        x='month', 
        y='total_rentals', 
        hue='year', 
        estimator='sum', 
        errorbar=None,
        marker='o', 
        palette='viridis', 
        ax=ax
    )
    ax.set_xlabel(None)
    ax.set_ylabel("Total Penyewaan")
    st.pyplot(fig)

with col_c:
    st.write("**Total Penyewaan per Bulan (Tahun ke Tahun)**")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        data=main_hour_df, 
        x='month', 
        y='total_rentals', 
        hue='year', 
        estimator='sum', 
        errorbar=None,
        marker='o', 
        palette='viridis', 
        ax=ax
    )
    ax.set_xlabel(None)
    ax.set_ylabel("Total Penyewaan")
    st.pyplot(fig)


# Pertanyaan 2: Faktor Lingkungan (Musim & Cuaca)
st.subheader("2. Pengaruh Lingkungan Terhadap Penyewaan")
col_e, col_f = st.columns(2)

with col_e:
    st.write("**Total Penyewaan Berdasarkan Musim**")
    season_df = create_season_rent_df(main_day_df)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=season_df.sort_values('total_rentals', ascending=False), 
        x='season', 
        y='total_rentals', 
        palette='viridis', 
        ax=ax
    )
    ax.set_ylabel("Total Penyewaan (juta)")
    st.pyplot(fig)

with col_f:
    st.write("**Total Penyewaan Berdasarkan Kondisi Cuaca**")
    weather_df = create_weather_rent_df(main_hour_df)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=weather_df.sort_values('total_rentals', ascending=False), 
        x='weathersit', 
        y='total_rentals', 
        palette='magma', 
        ax=ax
    )
    ax.set_ylabel("Total Penyewaan (juta)")
    st.pyplot(fig)

# Pertanyaan 3: Casual vs Registered
st.subheader("3. Karakteristik Pengguna: Casual vs Registered")
col_g, col_h = st.columns([1, 2])
col_i, col_j = st.columns(2)

with col_g:
    st.write("**Proporsi Tipe Pengguna**")
    user_type_df = create_user_type_df(main_day_df)
    fig, ax = plt.subplots()
    ax.pie(user_type_df['total_users'], labels=user_type_df['user_type'], autopct='%1.1f%%', colors=['#ff9999','#66b3ff'], startangle=90)
    st.pyplot(fig)

with col_h:
    st.write("**Tren Per Jam: Casual vs Registered**")
    hourly_user_df = create_hourly_user_df(main_hour_df)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=hourly_user_df, x='hour', y='casual_users', label='Casual', marker='o', ax=ax)
    sns.lineplot(data=hourly_user_df, x='hour', y='registered_users', label='Registered', marker='o', ax=ax)
    ax.set_xticks(range(0, 24))
    ax.set_ylabel("Jumlah Sewa")
    st.pyplot(fig)

with col_i:
    st.write("**Total Penyewaan per Hari: Casual vs Registered**")
    dailyuser_df = create_daily_user_df(main_hour_df)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=dailyuser_df,
        x='weekday', 
        y='value', 
        hue='variable', 
        palette='Set1'
)
    ax.set_ylabel("Total Penyewaan")
    ax.legend(title="Tipe Pengguna")
    st.pyplot(fig)

# Pertanyaan 4: Workingday vs Holiday
st.subheader("4. Pola Penyewaan: Hari Kerja vs Hari Libur")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    data=main_day_df, 
    x='workingday', 
    y='total_rentals', 
    estimator='sum',
    errorbar=None, 
    palette='Set2', 
    ax=ax
)
ax.set_xticklabels(['Weekend/Holiday', 'Working Day'])
ax.set_ylabel("Total Penyewaan (juta)")
ax.set_xlabel(None)
st.pyplot(fig)

st.caption('Copyright (c) Tazkiya AR 2026')