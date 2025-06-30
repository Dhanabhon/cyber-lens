import pandas as pd
import io

def generate_excel_report(df: pd.DataFrame) -> bytes:
    summary = {
        "Total Logs": len(df),
        "High Risk": (df["risk_level"] == "high").sum(),
        "Medium Risk": (df["risk_level"] == "medium").sum(),
        "Low Risk": (df["risk_level"] == "low").sum(),
        "Top 5 Risky IPs": df[df["risk_level"] != "low"]["ip"].value_counts().head(5).to_dict(),
    }

    summary_rows = [{"Metric": k, "Value": str(v)} for k, v in summary.items()]
    summary_df = pd.DataFrame(summary_rows)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        df.to_excel(writer, sheet_name="Detailed Logs", index=False)

    return output.getvalue()
