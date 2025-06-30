import pandas as pd

# Load simulated structured log
df = pd.read_csv("logs/simulated_log.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Create summary
summary = {
    "Total Logs": len(df),
    "High Risk": (df["risk_level"] == "high").sum(),
    "Medium Risk": (df["risk_level"] == "medium").sum(),
    "Low Risk": (df["risk_level"] == "low").sum(),
    "Top 5 Risky IPs": df[df["risk_level"] != "low"]["ip"].value_counts().head(5).to_dict(),
}

# Format summary as rows
summary_rows = [{"Metric": k, "Value": str(v)} for k, v in summary.items()]
summary_df = pd.DataFrame(summary_rows)

# Save to Excel
output_path = "output/cyberlens_summary_report.xlsx"
summary_df.to_excel(output_path, index=False)

print(f"[✓] Exported report to {output_path}")
