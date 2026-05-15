from __future__ import annotations

from io import BytesIO

import pandas as pd


def dataframe_to_excel_bytes(dataframe: pd.DataFrame, sheet_name: str = "Sheet1") -> bytes:
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name=sheet_name)
        worksheet = writer.sheets[sheet_name]

        for column in worksheet.columns:
            column_letter = column[0].column_letter
            max_length = max(len(str(cell.value or "")) for cell in column)
            worksheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 40)

    return output.getvalue()
