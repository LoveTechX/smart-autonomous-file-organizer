import pandas as pd
import matplotlib.pyplot as plt

# ======== LOAD DATA ========

file_path = "D:/AUTOMATION/file_logs.csv"

df = pd.read_csv(file_path)

# Convert timestamp
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# ======== STUDY VS CODING ========

category_counts = df["Category"].value_counts()

plt.figure()
category_counts.plot(kind="bar")
plt.title("Study vs Coding vs Other Activity")
plt.xlabel("Category")
plt.ylabel("File Count")
plt.show()


# ======== DAILY PRODUCTIVITY ========

df["Date"] = df["Timestamp"].dt.date
daily = df.groupby("Date").size()

plt.figure()
daily.plot()
plt.title("Daily Productivity")
plt.xlabel("Date")
plt.ylabel("Files Processed")
plt.show()


# ======== FILE TYPE ANALYSIS ========

ext_counts = df["Extension"].value_counts().head(10)

plt.figure()
ext_counts.plot(kind="bar")
plt.title("Most Used File Types")
plt.xlabel("Extension")
plt.ylabel("Count")
plt.show()


# ======== STORAGE ANALYSIS ========

df["SizeMB"] = df["Size(Bytes)"] / (1024 * 1024)
storage = df.groupby("Category")["SizeMB"].sum()

plt.figure()
storage.plot(kind="bar")
plt.title("Storage Usage by Category (MB)")
plt.xlabel("Category")
plt.ylabel("MB Used")
plt.show()

print("\nTop insights:")
print(category_counts.head())