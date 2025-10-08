import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Load the metrics file
df = pd.read_csv("../../data/silver/mock_issue_metrics.csv")

# Preprocess
df = df.dropna(subset=["t_created", "t_ready_for_qa", "t_done"])
df["t_created"] = pd.to_datetime(df["t_created"])
df["t_ready_for_qa"] = pd.to_datetime(df["t_ready_for_qa"])
df["t_done"] = pd.to_datetime(df["t_done"])
df["qa_squeeze_index"] = df["qa_window_days"] / (df["dev_cycle_days"] + df["qa_window_days"])

# Streamlit Dashboard
st.title("📊 SprintScope QA Metrics Dashboard")

# High-level metrics
col1, col2, col3 = st.columns(3)
col1.metric("🧠 Median Dev Days", f"{df['dev_cycle_days'].median():.1f}")
col2.metric("🔍 Median QA Days", f"{df['qa_window_days'].median():.1f}")
col3.metric("⚠️ % Late QA Entry", f"{(df['dev_lateness_ratio'] > 0.85).mean() * 100:.1f}%")

# Dev Lateness Histogram
st.subheader("📉 Dev Lateness Ratio Histogram")
fig1, ax1 = plt.subplots()
df["dev_lateness_ratio"].hist(bins=10, ax=ax1, color="skyblue")
ax1.set_title("Dev Lateness Distribution")
ax1.set_xlabel("Dev Lateness Ratio")
ax1.set_ylabel("Ticket Count")
st.pyplot(fig1)

# Dev vs QA scatterplot
st.subheader("⚖️ Dev vs QA Cycle")
fig2, ax2 = plt.subplots()
sns.scatterplot(data=df, x="dev_cycle_days", y="qa_window_days", hue="spill_indicator", ax=ax2)
ax2.set_title("Dev Days vs QA Days")
st.pyplot(fig2)

# QA Squeeze Index Chart
st.subheader("🩻 Top 5 QA-Squeezed Tickets")
top_squeezed = df.nsmallest(5, "qa_squeeze_index")
fig3, ax3 = plt.subplots()
sns.barplot(data=top_squeezed, x="qa_squeeze_index", y="issue_key", ax=ax3, palette="Reds_r")
ax3.set_title("Lowest QA Squeeze Index (Worst Squeezed)")
st.pyplot(fig3)

# Gantt-style timeline
st.subheader("📆 Dev + QA Time Breakdown")
fig4, ax4 = plt.subplots(figsize=(10, 6))
bar_data = df.sort_values("t_ready_for_qa").copy()
bar_data["issue"] = bar_data["issue_key"]
ax4.barh(bar_data["issue"], bar_data["dev_cycle_days"], label="Dev", color="#2ca02c")
ax4.barh(bar_data["issue"], bar_data["qa_window_days"], left=bar_data["dev_cycle_days"], label="QA", color="#ff7f0e")
ax4.set_xlabel("Days")
ax4.set_title("Dev + QA Duration")
ax4.legend()
st.pyplot(fig4)

# Raw Table
st.subheader("📋 Raw Issue Metrics Table")
st.dataframe(df)

# Export
st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="qa_metrics.csv")