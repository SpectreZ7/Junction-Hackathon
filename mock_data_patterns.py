import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("uber_mock_data.xlsx")
print(df.head())

# Quick cleaning example
df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time'] = pd.to_datetime(df['end_time'])
df['duration_min'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60

# Group by hour to see demand
df['hour'] = df['start_time'].dt.hour
hourly_demand = df.groupby('hour').size()

hourly_demand.plot(kind='bar', title='Hourly Ride Demand')
plt.show()
