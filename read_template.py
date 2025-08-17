import pandas as pd

# Read the Excel file
df = pd.read_excel("Fast2SMS WhatsApp Business Templates API 11-08-2025 12-58-55 pm.xlsx")

print("Template Data:")
print(df.to_string())

# Save as CSV for easier reading
df.to_csv("template_data.csv", index=False)
print("\nSaved as template_data.csv")