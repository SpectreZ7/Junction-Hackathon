import pandas as pd
import matplotlib.pyplot as plt

# Load the earner data from the correct path
df = pd.read_excel("data/uber_mock_data.xlsx")
print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())

# Analyze driver/earner patterns instead of ride patterns
print("\n=== DRIVER ANALYSIS ===")

# Driver status distribution
status_counts = df['status'].value_counts()
print("\nDriver Status Distribution:")
print(status_counts)

# Vehicle type analysis
vehicle_counts = df['vehicle_type'].value_counts()
print("\nVehicle Type Distribution:")
print(vehicle_counts)

# EV vs non-EV drivers
ev_counts = df['is_ev'].value_counts()
print("\nEV Distribution:")
print(ev_counts)

# Experience analysis
print("\nExperience Statistics:")
print(f"Average experience: {df['experience_months'].mean():.1f} months")
print(f"Experience range: {df['experience_months'].min()}-{df['experience_months'].max()} months")

# Rating analysis
print("\nRating Statistics:")
print(f"Average rating: {df['rating'].mean():.2f}")
print(f"Rating range: {df['rating'].min()}-{df['rating'].max()}")

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Status distribution
status_counts.plot(kind='bar', ax=axes[0,0], title='Driver Status Distribution', color='skyblue')
axes[0,0].tick_params(axis='x', rotation=45)

# Vehicle type distribution  
vehicle_counts.plot(kind='bar', ax=axes[0,1], title='Vehicle Type Distribution', color='lightgreen')
axes[0,1].tick_params(axis='x', rotation=45)

# Experience distribution
df['experience_months'].hist(bins=20, ax=axes[1,0], color='orange')
axes[1,0].set_title('Experience Distribution (months)')
axes[1,0].set_xlabel('Experience (months)')

# Rating distribution
df['rating'].hist(bins=20, ax=axes[1,1], color='pink')
axes[1,1].set_title('Rating Distribution')
axes[1,1].set_xlabel('Rating')

plt.tight_layout()
plt.show()

# Additional analysis: EV adoption by experience level
df['experience_level'] = pd.cut(df['experience_months'], bins=[0, 12, 36, 72, float('inf')], 
                               labels=['Newbie (0-12mo)', 'Intermediate (1-3yr)', 'Experienced (3-6yr)', 'Veteran (6yr+)'])

ev_by_experience = df.groupby('experience_level', observed=False)['is_ev'].value_counts(normalize=True).unstack()
print("\nEV Adoption by Experience Level:")
print(ev_by_experience)

# Plot EV adoption by experience
ev_by_experience.plot(kind='bar', stacked=True, title='EV Adoption by Experience Level')
plt.ylabel('Proportion')
plt.legend(title='Is EV', labels=['No', 'Yes'])
plt.tight_layout()
plt.show()
