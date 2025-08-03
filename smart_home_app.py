import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime

# Page setup
st.set_page_config(page_title="Smart Home Energy Dashboard", page_icon="⚡")
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", ["Home", "Log Data", "Dashboard"])

# Appliances and constants
appliances = {
    "Air Conditioner": 1.5,
    "Refrigerator": 0.2,
    "Washing Machine": 0.5,
    "Television": 0.1,
    "Microwave": 1.2,
    "Lights": 0.08
}
DATA_FILE = "clean_energy_data.csv"

# ------------------------
# HOME PAGE
# ------------------------
if page == "Home":
    st.title("⚡ Smart Home Energy Dashboard")
    st.markdown("Welcome, Suhani! This app helps track and visualize energy usage in your smart home.")
    st.image("https://media.giphy.com/media/3o7TKrQe5OMz3bKz3O/giphy.gif", use_container_width=True)
    st.markdown("---")
    st.markdown("⬅️ Use the sidebar to log your usage or explore your dashboard.")

# ------------------------
# LOG DATA PAGE
# ------------------------
elif page == "Log Data":
    st.header("📝 Log Your Own Usage")

    if "user_name" not in st.session_state:
        st.session_state["user_name"] = ""

    user_input = st.text_input("Enter your name:", st.session_state["user_name"])
    if user_input:
        st.session_state["user_name"] = user_input

    selected_appliances = st.multiselect("Which appliances are currently ON?", list(appliances.keys()))

    if st.button("Log My Energy Usage"):
        if not user_input:
            st.warning("⚠️ Please enter your name before logging.")
        elif not selected_appliances:
            st.warning("⚠️ Please select at least one appliance.")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_rows = []
            for appliance in selected_appliances:
                kw_rating = appliances[appliance]
                usage = round(kw_rating * random.uniform(0.8, 1.2), 2)
                log_rows.append([timestamp, user_input.strip(), appliance, 1, kw_rating, usage])

            df_user_log = pd.DataFrame(log_rows, columns=["Timestamp", "User", "Appliance", "Status", "KW_Rating", "Energy_kWh"])

            if os.path.exists(DATA_FILE):
                df_user_log.to_csv(DATA_FILE, mode='a', header=False, index=False)
            else:
                df_user_log.to_csv(DATA_FILE, index=False)

            st.success(f"✅ Usage logged for {user_input}!")

# ------------------------
# DASHBOARD PAGE
# ------------------------
elif page == "Dashboard":
    st.header("📊 Your Energy Dashboard")

    user_name = st.session_state.get("user_name", "").strip()
    st.write("🧪 DEBUG: Session name is →", user_name)

    if not user_name:
        st.warning("Please log your name first in 'Log Data' page.")
        st.stop()

    if not os.path.exists(DATA_FILE):
        st.info("No data file found yet. Please log some usage first.")
        st.stop()

    try:
        df = pd.read_csv(DATA_FILE, on_bad_lines='skip')
        df.columns = ["Timestamp", "User", "Appliance", "Status", "KW_Rating", "Energy_kWh"][:len(df.columns)]
        df = df.dropna()
        df["User"] = df["User"].astype(str).str.strip()
        st.write("🧪 DEBUG: Users in file →", df["User"].unique())

        # Match ignoring case and extra spaces
        user_df = df[df["User"].str.lower() == user_name.lower()]

    except Exception as e:
        st.error("❌ Error reading data file.")
        st.code(str(e))
        st.stop()

    if user_df.empty:
        st.info("No data logged yet for you. Go to 'Log Data' page and add some!")
        st.stop()

    st.subheader(f"🔍 Recent Logs for {user_name}")
    st.dataframe(user_df.tail(10))

    total_kwh = user_df["Energy_kWh"].sum()
    cost = total_kwh * 8

    st.metric("🔋 Total Energy Used (kWh)", f"{total_kwh:.2f}")
    st.metric("💸 Estimated Cost (INR)", f"₹{cost:.2f}")

    st.subheader("⚠️ Energy Alerts")
    if total_kwh > 10:
        st.error("⚡ High energy usage detected! Consider turning off unused appliances.")
    elif total_kwh > 5:
        st.warning("⚠️ Moderate energy consumption. Monitor regularly.")
    else:
        st.success("✅ Energy usage is within optimal range.")

    st.subheader("📊 Usage per Appliance")
    st.bar_chart(user_df.groupby("Appliance")["Energy_kWh"].sum())

    st.subheader("📈 Energy Usage Over Time")
    user_df["Timestamp"] = pd.to_datetime(user_df["Timestamp"])
    chart_df = user_df.sort_values("Timestamp").groupby("Timestamp")["Energy_kWh"].sum()
    st.line_chart(chart_df)


