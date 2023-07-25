# -*- coding: utf-8 

import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import numpy as np

try:
    # Functions
    def show_success_message():
        messagebox.showinfo("Success", f"Reporte actualizado correctamente")


    def csv_files_request(name):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title=f"Seleccionar archivo {name}", filetypes=[("CSV files", "*.csv")])

        if file_path:
            print(f"Seleccionar archivo {name}: {file_path}")

            # Read the CSV file
            df = pd.read_csv(file_path, encoding='latin1')
            df.columns = df.columns.str.replace('ï»¿', '') 
            df.columns = df.columns.str.replace(' (ï¿½)', '')
            # Print the DataFrame
            return df
        

    # Read the Excel file into a DataFrame
    df = csv_files_request("File")
    # pick_df = pd.read_csv('')

    df['order value'] = df['order value'].str.replace('$', '').str.replace(',', '').astype(float)

    df = df[df.duplicated() == False]

    # Assuming you have a DataFrame named 'df' with columns 'Backorder Aging' and 'On Hold Aging'

    df['Replenishment'] = 0  # Create a new column 'Replenishment' and initialize it with 0

    # Use pandas' vectorized operations to set values based on conditions
    df.loc[(df['Backorder Aging'] != '') & (df['On Hold Aging'] != ''), 'Replenishment'] = (df['Backorder Aging'] == df['On Hold Aging']).astype(int)

    # If you want to create a new DataFrame with only the 'Replenishment' column, you can use:
    replenishment_df = df[['Replenishment']].copy()

    # Assuming you have a DataFrame named 'df' with columns 'Company', 'Received Date', and 'Mex Warehouse Departure Date'

    df['Exported Same Day'] = np.where(df['company'].isnull(), np.nan, np.where(pd.to_datetime(df['Received Date']).dt.date == pd.to_datetime(df['Mex Warehouse Departure Date']).dt.date, 1, 0))

    # Assuming you have a DataFrame named 'df' with columns 'Company' and 'Received Date'
    df['Received Date'] = pd.to_datetime(df['Received Date'])

    df['Weekend Orders'] =  (df['Received Date'].dt.weekday.isin([5, 6]) & df['company'].notnull()).astype(int)

    # Assuming you have a DataFrame named 'df' with columns 'Company' and 'Received Date'

    # Perform the desired calculations
    weekday_condition = df['Received Date'].dt.weekday.eq(4)
    time_condition = (df['Received Date'].dt.hour + df['Received Date'].dt.minute / 60) > 13

    # Create the 'After cut-off' column based on the conditions
    df['After cut off'] = np.where(df['company'].notnull(), weekday_condition & time_condition, pd.NA)

    # Assuming you have a DataFrame named 'df' with columns 'Company' and 'Received Date'

    #weekday_condition_6 = df['Received Date'].dt.weekday.eq(5) & (df['Received Date'].dt.hour + df['Received Date'].dt.minute / 60) > 13
    #weekday_condition_7 = df['Received Date'].dt.weekday.eq(6)
    #weekday_condition_1 = df['Received Date'].dt.weekday.eq(0)

    # =ARRAYFORMULA(IF(A5:A="",,IFERROR(IFS((WEEKDAY(D5:D)=6)*(MOD(D5:D,1)>0.541666666666667),ROUNDDOWN(D5:D)+3,WEEKDAY(D5:D)=7,ROUNDDOWN(D5:D)+2,WEEKDAY(D5:D)=1,ROUNDDOWN(D5:D)+1),D5:D)))

    # Monday 0
    # Thursday 1
    # Wednesday 2
    # Tuesday 3
    # Friday 4
    # Saturday 5
    # Sunday 6

    def corrected_received_date(row):
        if pd.isnull(row['company']):
            return pd.NaT
        elif row['Received Date'].weekday() == 4 and row['Received Date'].hour > 13:
            return pd.Timestamp(row['Received Date'].date()) + pd.DateOffset(days=3)
        elif row['Received Date'].weekday() == 5:
            return pd.Timestamp(row['Received Date'].date()) + pd.DateOffset(days=2)
        elif row['Received Date'].weekday() == 6:
            return pd.Timestamp(row['Received Date'].date()) + pd.DateOffset(days=1)
        else:
            return row['Received Date']

    df['Corrected Received Date'] = df.apply(corrected_received_date, axis=1)

    # Assuming you have a DataFrame named 'df' with columns 'Company' and 'Label Created Date'

    df['Corrected Label Created'] = pd.to_datetime(df['Label Created Date']).where(df['company'].notnull(), pd.to_datetime('today') + pd.Timedelta(days=0.5))

    # Assuming you have a DataFrame named 'df' with a column 'Status'

    df['Real Orders'] = np.where(df['status'].isin(['Backorder', 'Cancelled', 'Re Stock', 'Re Stocked']), 0, 1)

    # Assuming you have a DataFrame named 'df' with columns 'Corrected Label Created', 'Received Date', and 'On Hold Aging'

    #df['PackingTime'] = np.where(df['Corrected Label Created'].isnull(), pd.NA, ((df['Corrected Label Created'] - df['Received Date']).dt.total_seconds() / 3600) - (df['On Hold Aging'] / 60))

    df['PackingTime'] = ((df['Corrected Label Created'] - df['Received Date']).dt.total_seconds() / 3600).fillna(0)# - df['On Hold Aging'] .fillna(0)/ 60

    """
    ### Aging Time Discrepancy"""

    test = df[["company","order number","Received Date","Corrected Label Created","PackingTime","On Hold Aging","Backorder Aging"]].head(200)
    test[test["On Hold Aging"].notna()]

    # Assuming you have a DataFrame named 'df' with columns 'Company', 'Mex Warehouse Departure Date', and 'Corrected Label Created'

    # Convert the 'Mex Warehouse Departure Date' and 'Corrected Label Created' columns to datetime type
    df['Mex Warehouse Departure Date'] = pd.to_datetime(df['Mex Warehouse Departure Date'])
    df['Corrected Label Created'] = pd.to_datetime(df['Corrected Label Created'])

    # Perform the subtraction and calculate the ShipMXTime
    df['ShipMXTime'] = ((df['Mex Warehouse Departure Date'] - df['Corrected Label Created']).dt.total_seconds() / 3600).fillna(0)

    # Assuming you have a DataFrame named 'df' with columns 'Company', 'Mex Warehouse Departure Date', and 'USA Warehouse Arrival Date'

    # Convert the 'Mex Warehouse Departure Date' and 'USA Warehouse Arrival Date' columns to datetime type
    df['Mex Warehouse Departure Date'] = pd.to_datetime(df['Mex Warehouse Departure Date'])
    df['USA Warehouse Arrival Date'] = pd.to_datetime(df['USA Warehouse Arrival Date'])

    # Perform the subtraction and calculate the In Transit Time
    df['In Transit Time'] = ((df['USA Warehouse Arrival Date'] - df['Mex Warehouse Departure Date']).dt.total_seconds() / 3600).fillna(0)

    df[["company","status","order number","Mex Warehouse Departure Date","USA Warehouse Arrival Date","In Transit Time"]].head(200)

    # Assuming you have a DataFrame named 'df' with columns 'Company', 'USA Warehouse Arrival Date', and 'Carrier Delivery Date'

    # Convert the 'USA Warehouse Arrival Date' and 'Carrier Delivery Date' columns to datetime type
    df['USA Warehouse Arrival Date'] = pd.to_datetime(df['USA Warehouse Arrival Date'])
    df['Carrier Delivery Date'] = pd.to_datetime(df['Carrier Delivery Date'])

    # Perform the subtraction and calculate the ShipUSATime
    df['ShipUSATime'] = ((df['Carrier Delivery Date'] - df['USA Warehouse Arrival Date']).dt.total_seconds() / 3600).fillna(0)

    df[["company","status","order number","Carrier Delivery Date","USA Warehouse Arrival Date","ShipUSATime"]].head(200)

    # Assuming you have a DataFrame named 'df' with a column 'Label Created Date'

    # Convert the 'Label Created Date' column to datetime type
    df['Label Created Date'] = pd.to_datetime(df['Label Created Date'])

    # Extract the date portion using floor('D') and assign it to a new column
    df['Rounded Label Created Date'] = df['Label Created Date'].dt.floor('D')

    # Assuming you have a DataFrame named 'df' with columns 'Company' and 'Received Date'

    df['Out of shift'] = np.where(df['company'].isnull(), pd.NA, ((df['Received Date'].dt.hour < 7) | (df['Received Date'].dt.hour >= 16)).astype(int))

    # Assuming 'df' is your pandas DataFrame and 'Label Created Date' is the column name

    # Monday 0
    # Thursday 1
    # Wednesday 2
    # Tuesday 3
    # Friday 4
    # Saturday 5
    # Sunday 6

    # Convert 'Benchmark' column back to datetime
    #df['Benchmark'] = pd.to_datetime(df['Benchmark'])

    df.columns

    def process_dates(row):
        if row["Received Date"].hour >= 13:
            if row["Received Date"].weekday() == 4:
                return (row['Received Date'] + pd.Timedelta(days=3)).replace(hour=13, minute=0, second=0, microsecond=0)
            elif row["Received Date"].weekday() == 5:
                return (row['Received Date'] + pd.Timedelta(days=2)).replace(hour=13, minute=0, second=0, microsecond=0)
            else:
                return (row['Received Date'] + pd.Timedelta(days=1)).replace(hour=13, minute=0, second=0, microsecond=0)
        else:
            return row['Received Date'].replace(hour=13, minute=0, second=0, microsecond=0)

    # Assuming your dataframe is named 'df'
    df['Processed Date'] = df.apply(process_dates, axis=1)

    from dateutil.relativedelta import relativedelta
    df['Received Date'] = pd.to_datetime(df['Received Date'])
    df['Mex Warehouse Departure Date'] = pd.to_datetime(df['Mex Warehouse Departure Date'])

    same_day_mask = df['Received Date'].dt.date == df['Mex Warehouse Departure Date'].dt.date
    df.loc[same_day_mask, 'Processed Date'] = df.loc[same_day_mask, 'Received Date'].apply(
        lambda x: x + relativedelta(days=0, hour=23, minute=59)
    )

    df['Processed Date'] = pd.to_datetime(df['Processed Date'], utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')

    df["Benchmark Validation"] = df["Processed Date"] > df["Mex Warehouse Departure Date"]

    df[["Received Date","Mex Warehouse Departure Date","Processed Date","Benchmark Validation"]]

    df[["Received Date","Mex Warehouse Departure Date","Processed Date","Benchmark Validation"]]

    #df['Benchmark'] = df['Benchmark'].apply(lambda x: x.replace(hour=13, minute=0, second=0, microsecond=0))

    # Assuming you have two DataFrames: 'df' with column 'Company', and 'site_df' with columns 'Customer' and 'Site'
    site_json = [
        {
            "company": "PINNACLE BRAND GROUP INC",
            "Site": "GENESIS"
        },
        {
            "company": "NAKED WOLFE LIMITED",
            "Site": "ARCA"
        },
        {
            "company": "TRU GRIT FITNESS LLC",
            "Site": "ARCA"
        },
        {
            "company": "EJAM INC",
            "Site": "GENESIS"
        },
        {
            "company": "PARAVEL INC",
            "Site": "ARCA"
        },
        {
            "company": "HAMMITT INC",
            "Site": "GENESIS"
        },
        {
            "company": "PHONESOAP LLC",
            "Site": "GENESIS"
        },
        {
            "company": "ZOIC",
            "Site": "GENESIS"
        },
        {
            "company": "UNCHARTED SUPPLY COMPANY",
            "Site": "GENESIS"
        },
        {
            "company": "JULIE ANN ELLIOT IN FIORE LLC",
            "Site": "ALPHA"
        },
        {
            "company": "AXION LLC",
            "Site": "GENESIS"
        },
        {
            "company": "LOLA GETS INC",
            "Site": "GENESIS"
        },
        {
            "company": "ATR BRANDS LIMITED",
            "Site": "ARCA"
        },
        {
            "company": "BEXCO ENTERPRISES INC",
            "Site": "ARCA"
        },
        {
            "company": "G-GLOBAL LOGISTICS INC",
            "Site": "NA"
        },
        {
            "company": "JUST ACCESS INC",
            "Site": "ARCA"
        },
        {
            "company": "CHARLY USA LLC",
            "Site": "ARCA"
        },
        {
            "company": "GOLDEN DRAGON ASSOCIATION INCDBA GOLDEN LIGHTING",
            "Site": "ARCA"
        },
        {
            "company": "XCEL BRANDS INC",
            "Site": "GENESIS"
        },
        {
            "company": "DECKED LLC",
            "Site": "ALPHA"
        },
        {
            "company": "FAMOSA NORTH AMERICA INC",
            "Site": "ARCA"
        },
        {
            "company": "JEG HOLDCO LLC",
            "Site": "GENESIS"
        },
        {
            "company": "OTG SURPLUS LLC",
            "Site": "GENESIS"
        },
        {
            "company": "ACRONYM LLC",
            "Site": "GENESIS"
        }
    ]

    site_df = pd.DataFrame(site_json)

    # Assuming you have the main DataFrame named 'df' and the SITE DataFrame named 'site_df'

    # Perform the merge based on the 'Company' column
    df = df.merge(site_df, left_on='company', right_on='company', how='left')

    # Rename the merged column as 'SITE'
    df.rename(columns={'Site': 'SITE'}, inplace=True)

    """### PackingTime"""

    df.loc[df['PackingTime'].apply(lambda x: True if x == 0 else False),"Packing_Time_Type"] = "N/A"
    df.loc[df['PackingTime'].apply(lambda x: True if 0 < x <= 12 else False),"Packing_Time_Type"] = "0 < PackTime <= 12"
    df.loc[df['PackingTime'].apply(lambda x: True if 12 < x <= 24 else False),"Packing_Time_Type"] = "12 < PackTime <= 24"
    df.loc[df['PackingTime'].apply(lambda x: True if 24 < x <= 48 else False),"Packing_Time_Type"] = "24 < PackTime <= 48"
    df.loc[df['PackingTime'].apply(lambda x: True if 48 < x <= 72 else False),"Packing_Time_Type"] = "48 < PackTime <= 72"
    df.loc[df['PackingTime'].apply(lambda x: True if x > 72 else False),"Packing_Time_Type"] = "PackTime > 72"

    """### ShipMXTime"""

    df.loc[df['ShipMXTime'].apply(lambda x: True if x == 0 else False),"ShipMX_Time_Type"] = "N/A"
    df.loc[df['ShipMXTime'].apply(lambda x: True if 0 < x <= 12 else False),"ShipMX_Time_Type"] = "0 < ShipMXTime <= 12"
    df.loc[df['ShipMXTime'].apply(lambda x: True if 12 < x <= 24 else False),"ShipMX_Time_Type"] = "12 < ShipMXTime <= 24"
    df.loc[df['ShipMXTime'].apply(lambda x: True if 24 < x <= 48 else False),"ShipMX_Time_Type"] = "24 < ShipMXTime <= 48"
    df.loc[df['ShipMXTime'].apply(lambda x: True if 48 < x <= 72 else False),"ShipMX_Time_Type"] = "48 < ShipMXTime <= 72"
    df.loc[df['ShipMXTime'].apply(lambda x: True if x > 72 else False),"ShipMX_Time_Type"] = "ShipMXTime > 72"

    df[df["ShipMX_Time_Type"].isna()]

    """### In Transit Time"""

    df.loc[df['In Transit Time'].apply(lambda x: True if x == 0 else False),"InTransit_Time_Type"] = "N/A"
    df.loc[df['In Transit Time'].apply(lambda x: True if 0 < x <= 12 else False),"InTransit_Time_Type"] = "0 < In Transit Time <= 12"
    df.loc[df['In Transit Time'].apply(lambda x: True if 12 < x <= 24 else False),"InTransit_Time_Type"] = "12 < In Transit Time <= 24"
    df.loc[df['In Transit Time'].apply(lambda x: True if 24 < x <= 48 else False),"InTransit_Time_Type"] = "24 < In Transit Time <= 48"
    df.loc[df['In Transit Time'].apply(lambda x: True if 48 < x <= 72 else False),"InTransit_Time_Type"] = "48 < In Transit Time <= 72"
    df.loc[df['In Transit Time'].apply(lambda x: True if x > 72 else False),"InTransit_Time_Type"] = "In Transit Time > 72"

    df[df["InTransit_Time_Type"].isna()]

    """### ShipUSATime"""

    df.loc[df['ShipUSATime'].apply(lambda x: True if x == 0 else False),"ShipUSATime_Type"] = "N/A"
    df.loc[df['ShipUSATime'].apply(lambda x: True if 0 < x <= 12 else False),"ShipUSATime_Type"] = "0 < ShipUSATime <= 12"
    df.loc[df['ShipUSATime'].apply(lambda x: True if 12 < x <= 24 else False),"ShipUSATime_Type"] = "12 < ShipUSATime <= 24"
    df.loc[df['ShipUSATime'].apply(lambda x: True if 24 < x <= 48 else False),"ShipUSATime_Type"] = "24 < ShipUSATime <= 48"
    df.loc[df['ShipUSATime'].apply(lambda x: True if 48 < x <= 72 else False),"ShipUSATime_Type"] = "48 < ShipUSATime <= 72"
    df.loc[df['ShipUSATime'].apply(lambda x: True if x > 72 else False),"ShipUSATime_Type"] = "ShipUSATime > 72"

    df[df["ShipUSATime_Type"].isna()]

    date_columns = [col_name for col_name in df.columns if df[col_name].dtype == 'datetime64[ns]']

    for col_name in date_columns:
        print(f"{col_name}: {col_name.lower().find('date') >= 0}")

    df["Rounded Received Date"] = df["Received Date"].apply(lambda x: x.date())
    df["Rounded Mex Warehouse Departure Date"] = df["Mex Warehouse Departure Date"].apply(lambda x: x.date())
    df["Rounded USA Warehouse Arrival Date"] = df["USA Warehouse Arrival Date"].apply(lambda x: x.date())
    df["Rounded Carrier Delivery Date"] = df["Carrier Delivery Date"].apply(lambda x: x.date())
    df["Rounded Label Created Date"] = df["Label Created Date"].apply(lambda x: x.date())
    df["Rounded Corrected Received Date"] = df["Corrected Received Date"].apply(lambda x: x.date())
    df["Rounded Corrected Label Created"] = df["Corrected Label Created"].apply(lambda x: x.date())

    df["Received Date Weeknumber"] = df["Received Date"].dt.isocalendar().week
    df["Received Date Month"] = df["Received Date"].dt.month

    df[["Received Date Weeknumber","Received Date Month"]]

    print(df.columns)

    df.rename(columns={"Requested Quantity (�)":"Requested Quantity","Picked Quantity (�)":"Picked Quantity","Validated Quantity (�)":"Validated Quantity"},inplace=True)

    print(df.columns)

    # Assuming you have a DataFrame named 'df' with a column 'PackingTime'

    #df['Packtime < 6 %'] = df['PackingTime'].apply(lambda x: 1 if pd.notnull(x) and x <= 6 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'PackingTime'

    #df['Packtime < 12 %'] = df['PackingTime'].apply(lambda x: 1 if pd.notnull(x) and 6 < x <= 12 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'PackingTime'

    #df['Packtime < 24 %'] = df['PackingTime'].apply(lambda x: 1 if pd.notnull(x) and 12 < x <= 24 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'PackingTime'

    #df['Packtime < 48 %'] = df['PackingTime'].apply(lambda x: 1 if pd.notnull(x) and 24 < x <= 48 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'PackingTime'

    #df['Packtime < 72 %'] = df['PackingTime'].apply(lambda x: 1 if pd.notnull(x) and 48 < x <= 72 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'PackingTime'

    #df['Packtime > 72 %'] = df['PackingTime'].apply(lambda x: 1 if pd.notnull(x) and x > 72 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'ShipMXTime'

    #df['ShipMXTime < 24 %'] = df['ShipMXTime'].apply(lambda x: 1 if pd.notnull(x) and 0 <= x <= 24 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'ShipMXTime'

    #df['ShipMXTime < 48 %'] = df['ShipMXTime'].apply(lambda x: 1 if pd.notnull(x) and 24 < x <= 48 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'ShipMXTime'

    #df['ShipMXTime < 72 %'] = df['ShipMXTime'].apply(lambda x: 1 if pd.notnull(x) and 48 < x <= 72 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'ShipMXTime'

    #df['ShipMXTime > 72 %'] = df['ShipMXTime'].apply(lambda x: 1 if pd.notnull(x) and x > 72 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'In Transit Time'

    #df['InTransitTime < 24'] = df['In Transit Time'].apply(lambda x: 1 if pd.notnull(x) and 0 <= x <= 24 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'In Transit Time'

    #df['InTransitTime < 48'] = df['In Transit Time'].apply(lambda x: 1 if pd.notnull(x) and 24 < x <= 48 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'In Transit Time'

    #df['InTransitTime < 72'] = df['In Transit Time'].apply(lambda x: 1 if pd.notnull(x) and 48 < x <= 72 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'In Transit Time'

    #df['InTransitTime > 72'] = df['In Transit Time'].apply(lambda x: 1 if pd.notnull(x) and x > 72 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'ShipUSATime'

    #df['ShipUSATime < 24'] = df['ShipUSATime'].apply(lambda x: 1 if pd.notnull(x) and 0 <= x <= 24 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'ShipUSATime'

    #df['ShipUSATime < 48'] = df['ShipUSATime'].apply(lambda x: 1 if pd.notnull(x) and 24 < x <= 48 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'ShipUSATime'

    #df['ShipUSATime < 72'] = df['ShipUSATime'].apply(lambda x: 1 if pd.notnull(x) and 48 < x <= 72 else 0)

    # Assuming you have a DataFrame named 'df' with a column 'ShipUSATime'

    #df['ShipUSATime > 72'] = df['ShipUSATime'].apply(lambda x: 1 if pd.notnull(x) and x > 72 else 0)

    """# Picker Report"""

    #picker_report = pd.read_csv('https://drive.google.com/file/d/1QFM00LqLPgFb22KCQdb1xWHWFauGSBi2/view?usp=drive_link')

    #import os

    #dir_path = r"/content/drive/MyDrive/Colab Notebooks/ReporteProductividad/Files/PickingReports"



    #save_csv = pd.DataFrame(df).to_csv(f"{new_directory}OnHands_{folder_name}.csv")

    #picker_report = concat_files(dir_path)

    #picker_report.rename(columns={"order":"order number","FileName":"company","start":"Start Picking Date","end":"End Picking Date","Time Processing":"Picking Time Processing"},inplace=True)
    #display(picker_report)

    #picker_report['Start Picking Date'] = pd.to_datetime(picker_report['Start Picking Date'])
    #picker_report["Start Picking Date"] = picker_report['Start Picking Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    #picker_report['End Picking Date'] = pd.to_datetime(picker_report['End Picking Date'])
    #picker_report["End Picking Date"] = picker_report['End Picking Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

    #picker_report

    """### Merge Picker Report and Orders Report"""

    #df = df.merge(picker_report, left_on=['order number',"company"], right_on=['order number',"company"], how='left')

    def categorize_order_type(df):
        df.loc[df["Requested Quantity"] <= 10, "Order Type"] = "Ecomm (1-10)"
        df.loc[(df["Requested Quantity"] > 10) & (df["Requested Quantity"] <= 50), "Order Type"] = "Small (11-50)"
        df.loc[(df["Requested Quantity"] > 50) & (df["Requested Quantity"] <= 250), "Order Type"] = "Medium (51-250)"
        df.loc[(df["Requested Quantity"] > 250) & (df["Requested Quantity"] <= 1000), "Order Type"] = "Large (251-1000)"
        df.loc[df["Requested Quantity"] > 1000, "Order Type"] = "Giant (>1000)"
        return df

    df = categorize_order_type(df)

    #df.loc[df["End Picking Date"].isna(),["order number","End Picking Date","company","Received Date"]]

    df.columns = df.columns.str.replace(' ', '_')

    df.columns

    """# Horas pagadas"""

    paid_hours = {"NAKED WOLFE LIMITED":	0.107,
                "FAMOSA NORTH AMERICA INC":	0.178,
                "PARAVEL INC":	0.151,
                "TRU GRIT FITNESS LLC":	0.082,
                "JUST ACCESS INC":	0.155,
                "BEXCO ENTERPRISES INC":	0.309,
                "CHARLY USA LLC":	0.1032991529,
                "HAMMITT INC":	0.1153,
                "EJAM INC":	0.0397250997,
                "UNCHARTED SUPPLY COMPANY":	0.0881,
                "ZOIC":	0.0686,
                "AXION LLC":	0.09021,
                "WCo":	0.09019021392,
                "ATR BRANDS LIMITED":	0.1896296296,
                "PINNACLE BRAND GROUP INC":	0.09021,
                "XCEL BRANDS INC":	0.0686
                }

    paid_hours_df = pd.DataFrame(list(paid_hours.items()), columns=["company", "Rate"])

    df.columns

    df = df.merge(paid_hours_df, on="company", how="left")
    df["Paid_Hours"] = df["Rate"] * df["Validated_Quantity"]

    """### Carrier Service"""

    df["Carrier_Service"] = df["Carrier_Service"].str.replace("�","")

    #world_cities = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/ReporteProductividad/Files/worldcities.csv')

    Country_codes = [{"name":"Afghanistan","dial_code":"+93","code":"AF"},{"name":"Aland Islands","dial_code":"+358","code":"AX"},{"name":"Albania","dial_code":"+355","code":"AL"},{"name":"Algeria","dial_code":"+213","code":"DZ"},{"name":"AmericanSamoa","dial_code":"+1684","code":"AS"},{"name":"Andorra","dial_code":"+376","code":"AD"},{"name":"Angola","dial_code":"+244","code":"AO"},{"name":"Anguilla","dial_code":"+1264","code":"AI"},{"name":"Antarctica","dial_code":"+672","code":"AQ"},{"name":"Antigua and Barbuda","dial_code":"+1268","code":"AG"},{"name":"Argentina","dial_code":"+54","code":"AR"},{"name":"Armenia","dial_code":"+374","code":"AM"},{"name":"Aruba","dial_code":"+297","code":"AW"},{"name":"Australia","dial_code":"+61","code":"AU"},{"name":"Austria","dial_code":"+43","code":"AT"},{"name":"Azerbaijan","dial_code":"+994","code":"AZ"},{"name":"Bahamas","dial_code":"+1242","code":"BS"},{"name":"Bahrain","dial_code":"+973","code":"BH"},{"name":"Bangladesh","dial_code":"+880","code":"BD"},{"name":"Barbados","dial_code":"+1246","code":"BB"},{"name":"Belarus","dial_code":"+375","code":"BY"},{"name":"Belgium","dial_code":"+32","code":"BE"},{"name":"Belize","dial_code":"+501","code":"BZ"},{"name":"Benin","dial_code":"+229","code":"BJ"},{"name":"Bermuda","dial_code":"+1441","code":"BM"},{"name":"Bhutan","dial_code":"+975","code":"BT"},{"name":"Bolivia, Plurinational State of","dial_code":"+591","code":"BO"},{"name":"Bosnia and Herzegovina","dial_code":"+387","code":"BA"},{"name":"Botswana","dial_code":"+267","code":"BW"},{"name":"Brazil","dial_code":"+55","code":"BR"},{"name":"British Indian Ocean Territory","dial_code":"+246","code":"IO"},{"name":"Brunei Darussalam","dial_code":"+673","code":"BN"},{"name":"Bulgaria","dial_code":"+359","code":"BG"},{"name":"Burkina Faso","dial_code":"+226","code":"BF"},{"name":"Burundi","dial_code":"+257","code":"BI"},{"name":"Cambodia","dial_code":"+855","code":"KH"},{"name":"Cameroon","dial_code":"+237","code":"CM"},{"name":"Canada","dial_code":"+1","code":"CA"},{"name":"Cape Verde","dial_code":"+238","code":"CV"},{"name":"Cayman Islands","dial_code":"+ 345","code":"KY"},{"name":"Central African Republic","dial_code":"+236","code":"CF"},{"name":"Chad","dial_code":"+235","code":"TD"},{"name":"Chile","dial_code":"+56","code":"CL"},{"name":"China","dial_code":"+86","code":"CN"},{"name":"Christmas Island","dial_code":"+61","code":"CX"},{"name":"Cocos (Keeling) Islands","dial_code":"+61","code":"CC"},{"name":"Colombia","dial_code":"+57","code":"CO"},{"name":"Comoros","dial_code":"+269","code":"KM"},{"name":"Congo","dial_code":"+242","code":"CG"},{"name":"Congo, The Democratic Republic of the Congo","dial_code":"+243","code":"CD"},{"name":"Cook Islands","dial_code":"+682","code":"CK"},{"name":"Costa Rica","dial_code":"+506","code":"CR"},{"name":"Cote d'Ivoire","dial_code":"+225","code":"CI"},{"name":"Croatia","dial_code":"+385","code":"HR"},{"name":"Cuba","dial_code":"+53","code":"CU"},{"name":"Cyprus","dial_code":"+357","code":"CY"},{"name":"Czech Republic","dial_code":"+420","code":"CZ"},{"name":"Denmark","dial_code":"+45","code":"DK"},{"name":"Djibouti","dial_code":"+253","code":"DJ"},{"name":"Dominica","dial_code":"+1767","code":"DM"},{"name":"Dominican Republic","dial_code":"+1849","code":"DO"},{"name":"Ecuador","dial_code":"+593","code":"EC"},{"name":"Egypt","dial_code":"+20","code":"EG"},{"name":"El Salvador","dial_code":"+503","code":"SV"},{"name":"Equatorial Guinea","dial_code":"+240","code":"GQ"},{"name":"Eritrea","dial_code":"+291","code":"ER"},{"name":"Estonia","dial_code":"+372","code":"EE"},{"name":"Ethiopia","dial_code":"+251","code":"ET"},{"name":"Falkland Islands (Malvinas)","dial_code":"+500","code":"FK"},{"name":"Faroe Islands","dial_code":"+298","code":"FO"},{"name":"Fiji","dial_code":"+679","code":"FJ"},{"name":"Finland","dial_code":"+358","code":"FI"},{"name":"France","dial_code":"+33","code":"FR"},{"name":"French Guiana","dial_code":"+594","code":"GF"},{"name":"French Polynesia","dial_code":"+689","code":"PF"},{"name":"Gabon","dial_code":"+241","code":"GA"},{"name":"Gambia","dial_code":"+220","code":"GM"},{"name":"Georgia","dial_code":"+995","code":"GE"},{"name":"Germany","dial_code":"+49","code":"DE"},{"name":"Ghana","dial_code":"+233","code":"GH"},{"name":"Gibraltar","dial_code":"+350","code":"GI"},{"name":"Greece","dial_code":"+30","code":"GR"},{"name":"Greenland","dial_code":"+299","code":"GL"},{"name":"Grenada","dial_code":"+1473","code":"GD"},{"name":"Guadeloupe","dial_code":"+590","code":"GP"},{"name":"Guam","dial_code":"+1671","code":"GU"},{"name":"Guatemala","dial_code":"+502","code":"GT"},{"name":"Guernsey","dial_code":"+44","code":"GG"},{"name":"Guinea","dial_code":"+224","code":"GN"},{"name":"Guinea-Bissau","dial_code":"+245","code":"GW"},{"name":"Guyana","dial_code":"+595","code":"GY"},{"name":"Haiti","dial_code":"+509","code":"HT"},{"name":"Holy See (Vatican City State)","dial_code":"+379","code":"VA"},{"name":"Honduras","dial_code":"+504","code":"HN"},{"name":"Hong Kong","dial_code":"+852","code":"HK"},{"name":"Hungary","dial_code":"+36","code":"HU"},{"name":"Iceland","dial_code":"+354","code":"IS"},{"name":"India","dial_code":"+91","code":"IN"},{"name":"Indonesia","dial_code":"+62","code":"ID"},{"name":"Iran, Islamic Republic of Persian Gulf","dial_code":"+98","code":"IR"},{"name":"Iraq","dial_code":"+964","code":"IQ"},{"name":"Ireland","dial_code":"+353","code":"IE"},{"name":"Isle of Man","dial_code":"+44","code":"IM"},{"name":"Israel","dial_code":"+972","code":"IL"},{"name":"Italy","dial_code":"+39","code":"IT"},{"name":"Jamaica","dial_code":"+1876","code":"JM"},{"name":"Japan","dial_code":"+81","code":"JP"},{"name":"Jersey","dial_code":"+44","code":"JE"},{"name":"Jordan","dial_code":"+962","code":"JO"},{"name":"Kazakhstan","dial_code":"+77","code":"KZ"},{"name":"Kenya","dial_code":"+254","code":"KE"},{"name":"Kiribati","dial_code":"+686","code":"KI"},{"name":"Korea, Democratic People's Republic of Korea","dial_code":"+850","code":"KP"},{"name":"Korea, Republic of South Korea","dial_code":"+82","code":"KR"},{"name":"Kuwait","dial_code":"+965","code":"KW"},{"name":"Kyrgyzstan","dial_code":"+996","code":"KG"},{"name":"Laos","dial_code":"+856","code":"LA"},{"name":"Latvia","dial_code":"+371","code":"LV"},{"name":"Lebanon","dial_code":"+961","code":"LB"},{"name":"Lesotho","dial_code":"+266","code":"LS"},{"name":"Liberia","dial_code":"+231","code":"LR"},{"name":"Libyan Arab Jamahiriya","dial_code":"+218","code":"LY"},{"name":"Liechtenstein","dial_code":"+423","code":"LI"},{"name":"Lithuania","dial_code":"+370","code":"LT"},{"name":"Luxembourg","dial_code":"+352","code":"LU"},{"name":"Macao","dial_code":"+853","code":"MO"},{"name":"Macedonia","dial_code":"+389","code":"MK"},{"name":"Madagascar","dial_code":"+261","code":"MG"},{"name":"Malawi","dial_code":"+265","code":"MW"},{"name":"Malaysia","dial_code":"+60","code":"MY"},{"name":"Maldives","dial_code":"+960","code":"MV"},{"name":"Mali","dial_code":"+223","code":"ML"},{"name":"Malta","dial_code":"+356","code":"MT"},{"name":"Marshall Islands","dial_code":"+692","code":"MH"},{"name":"Martinique","dial_code":"+596","code":"MQ"},{"name":"Mauritania","dial_code":"+222","code":"MR"},{"name":"Mauritius","dial_code":"+230","code":"MU"},{"name":"Mayotte","dial_code":"+262","code":"YT"},{"name":"Mexico","dial_code":"+52","code":"MX"},{"name":"Micronesia, Federated States of Micronesia","dial_code":"+691","code":"FM"},{"name":"Moldova","dial_code":"+373","code":"MD"},{"name":"Monaco","dial_code":"+377","code":"MC"},{"name":"Mongolia","dial_code":"+976","code":"MN"},{"name":"Montenegro","dial_code":"+382","code":"ME"},{"name":"Montserrat","dial_code":"+1664","code":"MS"},{"name":"Morocco","dial_code":"+212","code":"MA"},{"name":"Mozambique","dial_code":"+258","code":"MZ"},{"name":"Myanmar","dial_code":"+95","code":"MM"},{"name":"Namibia","dial_code":"+264","code":"NA"},{"name":"Nauru","dial_code":"+674","code":"NR"},{"name":"Nepal","dial_code":"+977","code":"NP"},{"name":"Netherlands","dial_code":"+31","code":"NL"},{"name":"Netherlands Antilles","dial_code":"+599","code":"AN"},{"name":"New Caledonia","dial_code":"+687","code":"NC"},{"name":"New Zealand","dial_code":"+64","code":"NZ"},{"name":"Nicaragua","dial_code":"+505","code":"NI"},{"name":"Niger","dial_code":"+227","code":"NE"},{"name":"Nigeria","dial_code":"+234","code":"NG"},{"name":"Niue","dial_code":"+683","code":"NU"},{"name":"Norfolk Island","dial_code":"+672","code":"NF"},{"name":"Northern Mariana Islands","dial_code":"+1670","code":"MP"},{"name":"Norway","dial_code":"+47","code":"NO"},{"name":"Oman","dial_code":"+968","code":"OM"},{"name":"Pakistan","dial_code":"+92","code":"PK"},{"name":"Palau","dial_code":"+680","code":"PW"},{"name":"Palestinian Territory, Occupied","dial_code":"+970","code":"PS"},{"name":"Panama","dial_code":"+507","code":"PA"},{"name":"Papua New Guinea","dial_code":"+675","code":"PG"},{"name":"Paraguay","dial_code":"+595","code":"PY"},{"name":"Peru","dial_code":"+51","code":"PE"},{"name":"Philippines","dial_code":"+63","code":"PH"},{"name":"Pitcairn","dial_code":"+872","code":"PN"},{"name":"Poland","dial_code":"+48","code":"PL"},{"name":"Portugal","dial_code":"+351","code":"PT"},{"name":"Puerto Rico","dial_code":"+1939","code":"PR"},{"name":"Qatar","dial_code":"+974","code":"QA"},{"name":"Romania","dial_code":"+40","code":"RO"},{"name":"Russia","dial_code":"+7","code":"RU"},{"name":"Rwanda","dial_code":"+250","code":"RW"},{"name":"Reunion","dial_code":"+262","code":"RE"},{"name":"Saint Barthelemy","dial_code":"+590","code":"BL"},{"name":"Saint Helena, Ascension and Tristan Da Cunha","dial_code":"+290","code":"SH"},{"name":"Saint Kitts and Nevis","dial_code":"+1869","code":"KN"},{"name":"Saint Lucia","dial_code":"+1758","code":"LC"},{"name":"Saint Martin","dial_code":"+590","code":"MF"},{"name":"Saint Pierre and Miquelon","dial_code":"+508","code":"PM"},{"name":"Saint Vincent and the Grenadines","dial_code":"+1784","code":"VC"},{"name":"Samoa","dial_code":"+685","code":"WS"},{"name":"San Marino","dial_code":"+378","code":"SM"},{"name":"Sao Tome and Principe","dial_code":"+239","code":"ST"},{"name":"Saudi Arabia","dial_code":"+966","code":"SA"},{"name":"Senegal","dial_code":"+221","code":"SN"},{"name":"Serbia","dial_code":"+381","code":"RS"},{"name":"Seychelles","dial_code":"+248","code":"SC"},{"name":"Sierra Leone","dial_code":"+232","code":"SL"},{"name":"Singapore","dial_code":"+65","code":"SG"},{"name":"Slovakia","dial_code":"+421","code":"SK"},{"name":"Slovenia","dial_code":"+386","code":"SI"},{"name":"Solomon Islands","dial_code":"+677","code":"SB"},{"name":"Somalia","dial_code":"+252","code":"SO"},{"name":"South Africa","dial_code":"+27","code":"ZA"},{"name":"South Sudan","dial_code":"+211","code":"SS"},{"name":"South Georgia and the South Sandwich Islands","dial_code":"+500","code":"GS"},{"name":"Spain","dial_code":"+34","code":"ES"},{"name":"Sri Lanka","dial_code":"+94","code":"LK"},{"name":"Sudan","dial_code":"+249","code":"SD"},{"name":"Suriname","dial_code":"+597","code":"SR"},{"name":"Svalbard and Jan Mayen","dial_code":"+47","code":"SJ"},{"name":"Swaziland","dial_code":"+268","code":"SZ"},{"name":"Sweden","dial_code":"+46","code":"SE"},{"name":"Switzerland","dial_code":"+41","code":"CH"},{"name":"Syrian Arab Republic","dial_code":"+963","code":"SY"},{"name":"Taiwan","dial_code":"+886","code":"TW"},{"name":"Tajikistan","dial_code":"+992","code":"TJ"},{"name":"Tanzania, United Republic of Tanzania","dial_code":"+255","code":"TZ"},{"name":"Thailand","dial_code":"+66","code":"TH"},{"name":"Timor-Leste","dial_code":"+670","code":"TL"},{"name":"Togo","dial_code":"+228","code":"TG"},{"name":"Tokelau","dial_code":"+690","code":"TK"},{"name":"Tonga","dial_code":"+676","code":"TO"},{"name":"Trinidad and Tobago","dial_code":"+1868","code":"TT"},{"name":"Tunisia","dial_code":"+216","code":"TN"},{"name":"Turkey","dial_code":"+90","code":"TR"},{"name":"Turkmenistan","dial_code":"+993","code":"TM"},{"name":"Turks and Caicos Islands","dial_code":"+1649","code":"TC"},{"name":"Tuvalu","dial_code":"+688","code":"TV"},{"name":"Uganda","dial_code":"+256","code":"UG"},{"name":"Ukraine","dial_code":"+380","code":"UA"},{"name":"United Arab Emirates","dial_code":"+971","code":"AE"},{"name":"United Kingdom","dial_code":"+44","code":"GB"},{"name":"United States","dial_code":"+1","code":"US"},{"name":"Uruguay","dial_code":"+598","code":"UY"},{"name":"Uzbekistan","dial_code":"+998","code":"UZ"},{"name":"Vanuatu","dial_code":"+678","code":"VU"},{"name":"Venezuela, Bolivarian Republic of Venezuela","dial_code":"+58","code":"VE"},{"name":"Vietnam","dial_code":"+84","code":"VN"},{"name":"Virgin Islands, British","dial_code":"+1284","code":"VG"},{"name":"Virgin Islands, U.S.","dial_code":"+1340","code":"VI"},{"name":"Wallis and Futuna","dial_code":"+681","code":"WF"},{"name":"Yemen","dial_code":"+967","code":"YE"},{"name":"Zambia","dial_code":"+260","code":"ZM"},{"name":"Zimbabwe","dial_code":"+263","code":"ZW"}]

    """### States Code"""

    states_code = [{"name":"Afghanistan","alpha-2":"AF","alpha-3":"AFG","country-code":"004","iso_3166-2":"ISO 3166-2:AF","region":"Asia","sub-region":"Southern Asia","intermediate-region":"","region-code":"142","sub-region-code":"034","intermediate-region-code":""},{"name":"Åland Islands","alpha-2":"AX","alpha-3":"ALA","country-code":"248","iso_3166-2":"ISO 3166-2:AX","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"Albania","alpha-2":"AL","alpha-3":"ALB","country-code":"008","iso_3166-2":"ISO 3166-2:AL","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Algeria","alpha-2":"DZ","alpha-3":"DZA","country-code":"012","iso_3166-2":"ISO 3166-2:DZ","region":"Africa","sub-region":"Northern Africa","intermediate-region":"","region-code":"002","sub-region-code":"015","intermediate-region-code":""},{"name":"American Samoa","alpha-2":"AS","alpha-3":"ASM","country-code":"016","iso_3166-2":"ISO 3166-2:AS","region":"Oceania","sub-region":"Polynesia","intermediate-region":"","region-code":"009","sub-region-code":"061","intermediate-region-code":""},{"name":"Andorra","alpha-2":"AD","alpha-3":"AND","country-code":"020","iso_3166-2":"ISO 3166-2:AD","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Angola","alpha-2":"AO","alpha-3":"AGO","country-code":"024","iso_3166-2":"ISO 3166-2:AO","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Middle Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"017"},{"name":"Anguilla","alpha-2":"AI","alpha-3":"AIA","country-code":"660","iso_3166-2":"ISO 3166-2:AI","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Antarctica","alpha-2":"AQ","alpha-3":"ATA","country-code":"010","iso_3166-2":"ISO 3166-2:AQ","region":"","sub-region":"","intermediate-region":"","region-code":"","sub-region-code":"","intermediate-region-code":""},{"name":"Antigua and Barbuda","alpha-2":"AG","alpha-3":"ATG","country-code":"028","iso_3166-2":"ISO 3166-2:AG","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Argentina","alpha-2":"AR","alpha-3":"ARG","country-code":"032","iso_3166-2":"ISO 3166-2:AR","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Armenia","alpha-2":"AM","alpha-3":"ARM","country-code":"051","iso_3166-2":"ISO 3166-2:AM","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Aruba","alpha-2":"AW","alpha-3":"ABW","country-code":"533","iso_3166-2":"ISO 3166-2:AW","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Australia","alpha-2":"AU","alpha-3":"AUS","country-code":"036","iso_3166-2":"ISO 3166-2:AU","region":"Oceania","sub-region":"Australia and New Zealand","intermediate-region":"","region-code":"009","sub-region-code":"053","intermediate-region-code":""},{"name":"Austria","alpha-2":"AT","alpha-3":"AUT","country-code":"040","iso_3166-2":"ISO 3166-2:AT","region":"Europe","sub-region":"Western Europe","intermediate-region":"","region-code":"150","sub-region-code":"155","intermediate-region-code":""},{"name":"Azerbaijan","alpha-2":"AZ","alpha-3":"AZE","country-code":"031","iso_3166-2":"ISO 3166-2:AZ","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Bahamas","alpha-2":"BS","alpha-3":"BHS","country-code":"044","iso_3166-2":"ISO 3166-2:BS","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Bahrain","alpha-2":"BH","alpha-3":"BHR","country-code":"048","iso_3166-2":"ISO 3166-2:BH","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Bangladesh","alpha-2":"BD","alpha-3":"BGD","country-code":"050","iso_3166-2":"ISO 3166-2:BD","region":"Asia","sub-region":"Southern Asia","intermediate-region":"","region-code":"142","sub-region-code":"034","intermediate-region-code":""},{"name":"Barbados","alpha-2":"BB","alpha-3":"BRB","country-code":"052","iso_3166-2":"ISO 3166-2:BB","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Belarus","alpha-2":"BY","alpha-3":"BLR","country-code":"112","iso_3166-2":"ISO 3166-2:BY","region":"Europe","sub-region":"Eastern Europe","intermediate-region":"","region-code":"150","sub-region-code":"151","intermediate-region-code":""},{"name":"Belgium","alpha-2":"BE","alpha-3":"BEL","country-code":"056","iso_3166-2":"ISO 3166-2:BE","region":"Europe","sub-region":"Western Europe","intermediate-region":"","region-code":"150","sub-region-code":"155","intermediate-region-code":""},{"name":"Belize","alpha-2":"BZ","alpha-3":"BLZ","country-code":"084","iso_3166-2":"ISO 3166-2:BZ","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Central America","region-code":"019","sub-region-code":"419","intermediate-region-code":"013"},{"name":"Benin","alpha-2":"BJ","alpha-3":"BEN","country-code":"204","iso_3166-2":"ISO 3166-2:BJ","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Bermuda","alpha-2":"BM","alpha-3":"BMU","country-code":"060","iso_3166-2":"ISO 3166-2:BM","region":"Americas","sub-region":"Northern America","intermediate-region":"","region-code":"019","sub-region-code":"021","intermediate-region-code":""},{"name":"Bhutan","alpha-2":"BT","alpha-3":"BTN","country-code":"064","iso_3166-2":"ISO 3166-2:BT","region":"Asia","sub-region":"Southern Asia","intermediate-region":"","region-code":"142","sub-region-code":"034","intermediate-region-code":""},{"name":"Bolivia (Plurinational State of)","alpha-2":"BO","alpha-3":"BOL","country-code":"068","iso_3166-2":"ISO 3166-2:BO","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Bonaire, Sint Eustatius and Saba","alpha-2":"BQ","alpha-3":"BES","country-code":"535","iso_3166-2":"ISO 3166-2:BQ","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Bosnia and Herzegovina","alpha-2":"BA","alpha-3":"BIH","country-code":"070","iso_3166-2":"ISO 3166-2:BA","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Botswana","alpha-2":"BW","alpha-3":"BWA","country-code":"072","iso_3166-2":"ISO 3166-2:BW","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Southern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"018"},{"name":"Bouvet Island","alpha-2":"BV","alpha-3":"BVT","country-code":"074","iso_3166-2":"ISO 3166-2:BV","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Brazil","alpha-2":"BR","alpha-3":"BRA","country-code":"076","iso_3166-2":"ISO 3166-2:BR","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"British Indian Ocean Territory","alpha-2":"IO","alpha-3":"IOT","country-code":"086","iso_3166-2":"ISO 3166-2:IO","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Brunei Darussalam","alpha-2":"BN","alpha-3":"BRN","country-code":"096","iso_3166-2":"ISO 3166-2:BN","region":"Asia","sub-region":"South-eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"035","intermediate-region-code":""},{"name":"Bulgaria","alpha-2":"BG","alpha-3":"BGR","country-code":"100","iso_3166-2":"ISO 3166-2:BG","region":"Europe","sub-region":"Eastern Europe","intermediate-region":"","region-code":"150","sub-region-code":"151","intermediate-region-code":""},{"name":"Burkina Faso","alpha-2":"BF","alpha-3":"BFA","country-code":"854","iso_3166-2":"ISO 3166-2:BF","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Burundi","alpha-2":"BI","alpha-3":"BDI","country-code":"108","iso_3166-2":"ISO 3166-2:BI","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Cabo Verde","alpha-2":"CV","alpha-3":"CPV","country-code":"132","iso_3166-2":"ISO 3166-2:CV","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Cambodia","alpha-2":"KH","alpha-3":"KHM","country-code":"116","iso_3166-2":"ISO 3166-2:KH","region":"Asia","sub-region":"South-eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"035","intermediate-region-code":""},{"name":"Cameroon","alpha-2":"CM","alpha-3":"CMR","country-code":"120","iso_3166-2":"ISO 3166-2:CM","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Middle Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"017"},{"name":"Canada","alpha-2":"CA","alpha-3":"CAN","country-code":"124","iso_3166-2":"ISO 3166-2:CA","region":"Americas","sub-region":"Northern America","intermediate-region":"","region-code":"019","sub-region-code":"021","intermediate-region-code":""},{"name":"Cayman Islands","alpha-2":"KY","alpha-3":"CYM","country-code":"136","iso_3166-2":"ISO 3166-2:KY","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Central African Republic","alpha-2":"CF","alpha-3":"CAF","country-code":"140","iso_3166-2":"ISO 3166-2:CF","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Middle Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"017"},{"name":"Chad","alpha-2":"TD","alpha-3":"TCD","country-code":"148","iso_3166-2":"ISO 3166-2:TD","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Middle Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"017"},{"name":"Chile","alpha-2":"CL","alpha-3":"CHL","country-code":"152","iso_3166-2":"ISO 3166-2:CL","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"China","alpha-2":"CN","alpha-3":"CHN","country-code":"156","iso_3166-2":"ISO 3166-2:CN","region":"Asia","sub-region":"Eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"030","intermediate-region-code":""},{"name":"Christmas Island","alpha-2":"CX","alpha-3":"CXR","country-code":"162","iso_3166-2":"ISO 3166-2:CX","region":"Oceania","sub-region":"Australia and New Zealand","intermediate-region":"","region-code":"009","sub-region-code":"053","intermediate-region-code":""},{"name":"Cocos (Keeling) Islands","alpha-2":"CC","alpha-3":"CCK","country-code":"166","iso_3166-2":"ISO 3166-2:CC","region":"Oceania","sub-region":"Australia and New Zealand","intermediate-region":"","region-code":"009","sub-region-code":"053","intermediate-region-code":""},{"name":"Colombia","alpha-2":"CO","alpha-3":"COL","country-code":"170","iso_3166-2":"ISO 3166-2:CO","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Comoros","alpha-2":"KM","alpha-3":"COM","country-code":"174","iso_3166-2":"ISO 3166-2:KM","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Congo","alpha-2":"CG","alpha-3":"COG","country-code":"178","iso_3166-2":"ISO 3166-2:CG","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Middle Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"017"},{"name":"Congo, Democratic Republic of the","alpha-2":"CD","alpha-3":"COD","country-code":"180","iso_3166-2":"ISO 3166-2:CD","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Middle Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"017"},{"name":"Cook Islands","alpha-2":"CK","alpha-3":"COK","country-code":"184","iso_3166-2":"ISO 3166-2:CK","region":"Oceania","sub-region":"Polynesia","intermediate-region":"","region-code":"009","sub-region-code":"061","intermediate-region-code":""},{"name":"Costa Rica","alpha-2":"CR","alpha-3":"CRI","country-code":"188","iso_3166-2":"ISO 3166-2:CR","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Central America","region-code":"019","sub-region-code":"419","intermediate-region-code":"013"},{"name":"Côte d'Ivoire","alpha-2":"CI","alpha-3":"CIV","country-code":"384","iso_3166-2":"ISO 3166-2:CI","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Croatia","alpha-2":"HR","alpha-3":"HRV","country-code":"191","iso_3166-2":"ISO 3166-2:HR","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Cuba","alpha-2":"CU","alpha-3":"CUB","country-code":"192","iso_3166-2":"ISO 3166-2:CU","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Curaçao","alpha-2":"CW","alpha-3":"CUW","country-code":"531","iso_3166-2":"ISO 3166-2:CW","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Cyprus","alpha-2":"CY","alpha-3":"CYP","country-code":"196","iso_3166-2":"ISO 3166-2:CY","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Czechia","alpha-2":"CZ","alpha-3":"CZE","country-code":"203","iso_3166-2":"ISO 3166-2:CZ","region":"Europe","sub-region":"Eastern Europe","intermediate-region":"","region-code":"150","sub-region-code":"151","intermediate-region-code":""},{"name":"Denmark","alpha-2":"DK","alpha-3":"DNK","country-code":"208","iso_3166-2":"ISO 3166-2:DK","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"Djibouti","alpha-2":"DJ","alpha-3":"DJI","country-code":"262","iso_3166-2":"ISO 3166-2:DJ","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Dominica","alpha-2":"DM","alpha-3":"DMA","country-code":"212","iso_3166-2":"ISO 3166-2:DM","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Dominican Republic","alpha-2":"DO","alpha-3":"DOM","country-code":"214","iso_3166-2":"ISO 3166-2:DO","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Ecuador","alpha-2":"EC","alpha-3":"ECU","country-code":"218","iso_3166-2":"ISO 3166-2:EC","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Egypt","alpha-2":"EG","alpha-3":"EGY","country-code":"818","iso_3166-2":"ISO 3166-2:EG","region":"Africa","sub-region":"Northern Africa","intermediate-region":"","region-code":"002","sub-region-code":"015","intermediate-region-code":""},{"name":"El Salvador","alpha-2":"SV","alpha-3":"SLV","country-code":"222","iso_3166-2":"ISO 3166-2:SV","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Central America","region-code":"019","sub-region-code":"419","intermediate-region-code":"013"},{"name":"Equatorial Guinea","alpha-2":"GQ","alpha-3":"GNQ","country-code":"226","iso_3166-2":"ISO 3166-2:GQ","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Middle Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"017"},{"name":"Eritrea","alpha-2":"ER","alpha-3":"ERI","country-code":"232","iso_3166-2":"ISO 3166-2:ER","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Estonia","alpha-2":"EE","alpha-3":"EST","country-code":"233","iso_3166-2":"ISO 3166-2:EE","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"Eswatini","alpha-2":"SZ","alpha-3":"SWZ","country-code":"748","iso_3166-2":"ISO 3166-2:SZ","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Southern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"018"},{"name":"Ethiopia","alpha-2":"ET","alpha-3":"ETH","country-code":"231","iso_3166-2":"ISO 3166-2:ET","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Falkland Islands (Malvinas)","alpha-2":"FK","alpha-3":"FLK","country-code":"238","iso_3166-2":"ISO 3166-2:FK","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Faroe Islands","alpha-2":"FO","alpha-3":"FRO","country-code":"234","iso_3166-2":"ISO 3166-2:FO","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"Fiji","alpha-2":"FJ","alpha-3":"FJI","country-code":"242","iso_3166-2":"ISO 3166-2:FJ","region":"Oceania","sub-region":"Melanesia","intermediate-region":"","region-code":"009","sub-region-code":"054","intermediate-region-code":""},{"name":"Finland","alpha-2":"FI","alpha-3":"FIN","country-code":"246","iso_3166-2":"ISO 3166-2:FI","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"France","alpha-2":"FR","alpha-3":"FRA","country-code":"250","iso_3166-2":"ISO 3166-2:FR","region":"Europe","sub-region":"Western Europe","intermediate-region":"","region-code":"150","sub-region-code":"155","intermediate-region-code":""},{"name":"French Guiana","alpha-2":"GF","alpha-3":"GUF","country-code":"254","iso_3166-2":"ISO 3166-2:GF","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"French Polynesia","alpha-2":"PF","alpha-3":"PYF","country-code":"258","iso_3166-2":"ISO 3166-2:PF","region":"Oceania","sub-region":"Polynesia","intermediate-region":"","region-code":"009","sub-region-code":"061","intermediate-region-code":""},{"name":"French Southern Territories","alpha-2":"TF","alpha-3":"ATF","country-code":"260","iso_3166-2":"ISO 3166-2:TF","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Gabon","alpha-2":"GA","alpha-3":"GAB","country-code":"266","iso_3166-2":"ISO 3166-2:GA","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Middle Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"017"},{"name":"Gambia","alpha-2":"GM","alpha-3":"GMB","country-code":"270","iso_3166-2":"ISO 3166-2:GM","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Georgia","alpha-2":"GE","alpha-3":"GEO","country-code":"268","iso_3166-2":"ISO 3166-2:GE","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Germany","alpha-2":"DE","alpha-3":"DEU","country-code":"276","iso_3166-2":"ISO 3166-2:DE","region":"Europe","sub-region":"Western Europe","intermediate-region":"","region-code":"150","sub-region-code":"155","intermediate-region-code":""},{"name":"Ghana","alpha-2":"GH","alpha-3":"GHA","country-code":"288","iso_3166-2":"ISO 3166-2:GH","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Gibraltar","alpha-2":"GI","alpha-3":"GIB","country-code":"292","iso_3166-2":"ISO 3166-2:GI","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Greece","alpha-2":"GR","alpha-3":"GRC","country-code":"300","iso_3166-2":"ISO 3166-2:GR","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Greenland","alpha-2":"GL","alpha-3":"GRL","country-code":"304","iso_3166-2":"ISO 3166-2:GL","region":"Americas","sub-region":"Northern America","intermediate-region":"","region-code":"019","sub-region-code":"021","intermediate-region-code":""},{"name":"Grenada","alpha-2":"GD","alpha-3":"GRD","country-code":"308","iso_3166-2":"ISO 3166-2:GD","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Guadeloupe","alpha-2":"GP","alpha-3":"GLP","country-code":"312","iso_3166-2":"ISO 3166-2:GP","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Guam","alpha-2":"GU","alpha-3":"GUM","country-code":"316","iso_3166-2":"ISO 3166-2:GU","region":"Oceania","sub-region":"Micronesia","intermediate-region":"","region-code":"009","sub-region-code":"057","intermediate-region-code":""},{"name":"Guatemala","alpha-2":"GT","alpha-3":"GTM","country-code":"320","iso_3166-2":"ISO 3166-2:GT","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Central America","region-code":"019","sub-region-code":"419","intermediate-region-code":"013"},{"name":"Guernsey","alpha-2":"GG","alpha-3":"GGY","country-code":"831","iso_3166-2":"ISO 3166-2:GG","region":"Europe","sub-region":"Northern Europe","intermediate-region":"Channel Islands","region-code":"150","sub-region-code":"154","intermediate-region-code":"830"},{"name":"Guinea","alpha-2":"GN","alpha-3":"GIN","country-code":"324","iso_3166-2":"ISO 3166-2:GN","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Guinea-Bissau","alpha-2":"GW","alpha-3":"GNB","country-code":"624","iso_3166-2":"ISO 3166-2:GW","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Guyana","alpha-2":"GY","alpha-3":"GUY","country-code":"328","iso_3166-2":"ISO 3166-2:GY","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Haiti","alpha-2":"HT","alpha-3":"HTI","country-code":"332","iso_3166-2":"ISO 3166-2:HT","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Heard Island and McDonald Islands","alpha-2":"HM","alpha-3":"HMD","country-code":"334","iso_3166-2":"ISO 3166-2:HM","region":"Oceania","sub-region":"Australia and New Zealand","intermediate-region":"","region-code":"009","sub-region-code":"053","intermediate-region-code":""},{"name":"Holy See","alpha-2":"VA","alpha-3":"VAT","country-code":"336","iso_3166-2":"ISO 3166-2:VA","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Honduras","alpha-2":"HN","alpha-3":"HND","country-code":"340","iso_3166-2":"ISO 3166-2:HN","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Central America","region-code":"019","sub-region-code":"419","intermediate-region-code":"013"},{"name":"Hong Kong","alpha-2":"HK","alpha-3":"HKG","country-code":"344","iso_3166-2":"ISO 3166-2:HK","region":"Asia","sub-region":"Eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"030","intermediate-region-code":""},{"name":"Hungary","alpha-2":"HU","alpha-3":"HUN","country-code":"348","iso_3166-2":"ISO 3166-2:HU","region":"Europe","sub-region":"Eastern Europe","intermediate-region":"","region-code":"150","sub-region-code":"151","intermediate-region-code":""},{"name":"Iceland","alpha-2":"IS","alpha-3":"ISL","country-code":"352","iso_3166-2":"ISO 3166-2:IS","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"India","alpha-2":"IN","alpha-3":"IND","country-code":"356","iso_3166-2":"ISO 3166-2:IN","region":"Asia","sub-region":"Southern Asia","intermediate-region":"","region-code":"142","sub-region-code":"034","intermediate-region-code":""},{"name":"Indonesia","alpha-2":"ID","alpha-3":"IDN","country-code":"360","iso_3166-2":"ISO 3166-2:ID","region":"Asia","sub-region":"South-eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"035","intermediate-region-code":""},{"name":"Iran (Islamic Republic of)","alpha-2":"IR","alpha-3":"IRN","country-code":"364","iso_3166-2":"ISO 3166-2:IR","region":"Asia","sub-region":"Southern Asia","intermediate-region":"","region-code":"142","sub-region-code":"034","intermediate-region-code":""},{"name":"Iraq","alpha-2":"IQ","alpha-3":"IRQ","country-code":"368","iso_3166-2":"ISO 3166-2:IQ","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Ireland","alpha-2":"IE","alpha-3":"IRL","country-code":"372","iso_3166-2":"ISO 3166-2:IE","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"Isle of Man","alpha-2":"IM","alpha-3":"IMN","country-code":"833","iso_3166-2":"ISO 3166-2:IM","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"Israel","alpha-2":"IL","alpha-3":"ISR","country-code":"376","iso_3166-2":"ISO 3166-2:IL","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Italy","alpha-2":"IT","alpha-3":"ITA","country-code":"380","iso_3166-2":"ISO 3166-2:IT","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Jamaica","alpha-2":"JM","alpha-3":"JAM","country-code":"388","iso_3166-2":"ISO 3166-2:JM","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Japan","alpha-2":"JP","alpha-3":"JPN","country-code":"392","iso_3166-2":"ISO 3166-2:JP","region":"Asia","sub-region":"Eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"030","intermediate-region-code":""},{"name":"Jersey","alpha-2":"JE","alpha-3":"JEY","country-code":"832","iso_3166-2":"ISO 3166-2:JE","region":"Europe","sub-region":"Northern Europe","intermediate-region":"Channel Islands","region-code":"150","sub-region-code":"154","intermediate-region-code":"830"},{"name":"Jordan","alpha-2":"JO","alpha-3":"JOR","country-code":"400","iso_3166-2":"ISO 3166-2:JO","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Kazakhstan","alpha-2":"KZ","alpha-3":"KAZ","country-code":"398","iso_3166-2":"ISO 3166-2:KZ","region":"Asia","sub-region":"Central Asia","intermediate-region":"","region-code":"142","sub-region-code":"143","intermediate-region-code":""},{"name":"Kenya","alpha-2":"KE","alpha-3":"KEN","country-code":"404","iso_3166-2":"ISO 3166-2:KE","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Kiribati","alpha-2":"KI","alpha-3":"KIR","country-code":"296","iso_3166-2":"ISO 3166-2:KI","region":"Oceania","sub-region":"Micronesia","intermediate-region":"","region-code":"009","sub-region-code":"057","intermediate-region-code":""},{"name":"Korea (Democratic People's Republic of)","alpha-2":"KP","alpha-3":"PRK","country-code":"408","iso_3166-2":"ISO 3166-2:KP","region":"Asia","sub-region":"Eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"030","intermediate-region-code":""},{"name":"Korea, Republic of","alpha-2":"KR","alpha-3":"KOR","country-code":"410","iso_3166-2":"ISO 3166-2:KR","region":"Asia","sub-region":"Eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"030","intermediate-region-code":""},{"name":"Kuwait","alpha-2":"KW","alpha-3":"KWT","country-code":"414","iso_3166-2":"ISO 3166-2:KW","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Kyrgyzstan","alpha-2":"KG","alpha-3":"KGZ","country-code":"417","iso_3166-2":"ISO 3166-2:KG","region":"Asia","sub-region":"Central Asia","intermediate-region":"","region-code":"142","sub-region-code":"143","intermediate-region-code":""},{"name":"Lao People's Democratic Republic","alpha-2":"LA","alpha-3":"LAO","country-code":"418","iso_3166-2":"ISO 3166-2:LA","region":"Asia","sub-region":"South-eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"035","intermediate-region-code":""},{"name":"Latvia","alpha-2":"LV","alpha-3":"LVA","country-code":"428","iso_3166-2":"ISO 3166-2:LV","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"Lebanon","alpha-2":"LB","alpha-3":"LBN","country-code":"422","iso_3166-2":"ISO 3166-2:LB","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Lesotho","alpha-2":"LS","alpha-3":"LSO","country-code":"426","iso_3166-2":"ISO 3166-2:LS","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Southern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"018"},{"name":"Liberia","alpha-2":"LR","alpha-3":"LBR","country-code":"430","iso_3166-2":"ISO 3166-2:LR","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Libya","alpha-2":"LY","alpha-3":"LBY","country-code":"434","iso_3166-2":"ISO 3166-2:LY","region":"Africa","sub-region":"Northern Africa","intermediate-region":"","region-code":"002","sub-region-code":"015","intermediate-region-code":""},{"name":"Liechtenstein","alpha-2":"LI","alpha-3":"LIE","country-code":"438","iso_3166-2":"ISO 3166-2:LI","region":"Europe","sub-region":"Western Europe","intermediate-region":"","region-code":"150","sub-region-code":"155","intermediate-region-code":""},{"name":"Lithuania","alpha-2":"LT","alpha-3":"LTU","country-code":"440","iso_3166-2":"ISO 3166-2:LT","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"Luxembourg","alpha-2":"LU","alpha-3":"LUX","country-code":"442","iso_3166-2":"ISO 3166-2:LU","region":"Europe","sub-region":"Western Europe","intermediate-region":"","region-code":"150","sub-region-code":"155","intermediate-region-code":""},{"name":"Macao","alpha-2":"MO","alpha-3":"MAC","country-code":"446","iso_3166-2":"ISO 3166-2:MO","region":"Asia","sub-region":"Eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"030","intermediate-region-code":""},{"name":"Madagascar","alpha-2":"MG","alpha-3":"MDG","country-code":"450","iso_3166-2":"ISO 3166-2:MG","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Malawi","alpha-2":"MW","alpha-3":"MWI","country-code":"454","iso_3166-2":"ISO 3166-2:MW","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Malaysia","alpha-2":"MY","alpha-3":"MYS","country-code":"458","iso_3166-2":"ISO 3166-2:MY","region":"Asia","sub-region":"South-eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"035","intermediate-region-code":""},{"name":"Maldives","alpha-2":"MV","alpha-3":"MDV","country-code":"462","iso_3166-2":"ISO 3166-2:MV","region":"Asia","sub-region":"Southern Asia","intermediate-region":"","region-code":"142","sub-region-code":"034","intermediate-region-code":""},{"name":"Mali","alpha-2":"ML","alpha-3":"MLI","country-code":"466","iso_3166-2":"ISO 3166-2:ML","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Malta","alpha-2":"MT","alpha-3":"MLT","country-code":"470","iso_3166-2":"ISO 3166-2:MT","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Marshall Islands","alpha-2":"MH","alpha-3":"MHL","country-code":"584","iso_3166-2":"ISO 3166-2:MH","region":"Oceania","sub-region":"Micronesia","intermediate-region":"","region-code":"009","sub-region-code":"057","intermediate-region-code":""},{"name":"Martinique","alpha-2":"MQ","alpha-3":"MTQ","country-code":"474","iso_3166-2":"ISO 3166-2:MQ","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Mauritania","alpha-2":"MR","alpha-3":"MRT","country-code":"478","iso_3166-2":"ISO 3166-2:MR","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Mauritius","alpha-2":"MU","alpha-3":"MUS","country-code":"480","iso_3166-2":"ISO 3166-2:MU","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Mayotte","alpha-2":"YT","alpha-3":"MYT","country-code":"175","iso_3166-2":"ISO 3166-2:YT","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Mexico","alpha-2":"MX","alpha-3":"MEX","country-code":"484","iso_3166-2":"ISO 3166-2:MX","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Central America","region-code":"019","sub-region-code":"419","intermediate-region-code":"013"},{"name":"Micronesia (Federated States of)","alpha-2":"FM","alpha-3":"FSM","country-code":"583","iso_3166-2":"ISO 3166-2:FM","region":"Oceania","sub-region":"Micronesia","intermediate-region":"","region-code":"009","sub-region-code":"057","intermediate-region-code":""},{"name":"Moldova, Republic of","alpha-2":"MD","alpha-3":"MDA","country-code":"498","iso_3166-2":"ISO 3166-2:MD","region":"Europe","sub-region":"Eastern Europe","intermediate-region":"","region-code":"150","sub-region-code":"151","intermediate-region-code":""},{"name":"Monaco","alpha-2":"MC","alpha-3":"MCO","country-code":"492","iso_3166-2":"ISO 3166-2:MC","region":"Europe","sub-region":"Western Europe","intermediate-region":"","region-code":"150","sub-region-code":"155","intermediate-region-code":""},{"name":"Mongolia","alpha-2":"MN","alpha-3":"MNG","country-code":"496","iso_3166-2":"ISO 3166-2:MN","region":"Asia","sub-region":"Eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"030","intermediate-region-code":""},{"name":"Montenegro","alpha-2":"ME","alpha-3":"MNE","country-code":"499","iso_3166-2":"ISO 3166-2:ME","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Montserrat","alpha-2":"MS","alpha-3":"MSR","country-code":"500","iso_3166-2":"ISO 3166-2:MS","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Morocco","alpha-2":"MA","alpha-3":"MAR","country-code":"504","iso_3166-2":"ISO 3166-2:MA","region":"Africa","sub-region":"Northern Africa","intermediate-region":"","region-code":"002","sub-region-code":"015","intermediate-region-code":""},{"name":"Mozambique","alpha-2":"MZ","alpha-3":"MOZ","country-code":"508","iso_3166-2":"ISO 3166-2:MZ","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Myanmar","alpha-2":"MM","alpha-3":"MMR","country-code":"104","iso_3166-2":"ISO 3166-2:MM","region":"Asia","sub-region":"South-eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"035","intermediate-region-code":""},{"name":"Namibia","alpha-2":"NA","alpha-3":"NAM","country-code":"516","iso_3166-2":"ISO 3166-2:NA","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Southern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"018"},{"name":"Nauru","alpha-2":"NR","alpha-3":"NRU","country-code":"520","iso_3166-2":"ISO 3166-2:NR","region":"Oceania","sub-region":"Micronesia","intermediate-region":"","region-code":"009","sub-region-code":"057","intermediate-region-code":""},{"name":"Nepal","alpha-2":"NP","alpha-3":"NPL","country-code":"524","iso_3166-2":"ISO 3166-2:NP","region":"Asia","sub-region":"Southern Asia","intermediate-region":"","region-code":"142","sub-region-code":"034","intermediate-region-code":""},{"name":"Netherlands","alpha-2":"NL","alpha-3":"NLD","country-code":"528","iso_3166-2":"ISO 3166-2:NL","region":"Europe","sub-region":"Western Europe","intermediate-region":"","region-code":"150","sub-region-code":"155","intermediate-region-code":""},{"name":"New Caledonia","alpha-2":"NC","alpha-3":"NCL","country-code":"540","iso_3166-2":"ISO 3166-2:NC","region":"Oceania","sub-region":"Melanesia","intermediate-region":"","region-code":"009","sub-region-code":"054","intermediate-region-code":""},{"name":"New Zealand","alpha-2":"NZ","alpha-3":"NZL","country-code":"554","iso_3166-2":"ISO 3166-2:NZ","region":"Oceania","sub-region":"Australia and New Zealand","intermediate-region":"","region-code":"009","sub-region-code":"053","intermediate-region-code":""},{"name":"Nicaragua","alpha-2":"NI","alpha-3":"NIC","country-code":"558","iso_3166-2":"ISO 3166-2:NI","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Central America","region-code":"019","sub-region-code":"419","intermediate-region-code":"013"},{"name":"Niger","alpha-2":"NE","alpha-3":"NER","country-code":"562","iso_3166-2":"ISO 3166-2:NE","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Nigeria","alpha-2":"NG","alpha-3":"NGA","country-code":"566","iso_3166-2":"ISO 3166-2:NG","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Niue","alpha-2":"NU","alpha-3":"NIU","country-code":"570","iso_3166-2":"ISO 3166-2:NU","region":"Oceania","sub-region":"Polynesia","intermediate-region":"","region-code":"009","sub-region-code":"061","intermediate-region-code":""},{"name":"Norfolk Island","alpha-2":"NF","alpha-3":"NFK","country-code":"574","iso_3166-2":"ISO 3166-2:NF","region":"Oceania","sub-region":"Australia and New Zealand","intermediate-region":"","region-code":"009","sub-region-code":"053","intermediate-region-code":""},{"name":"North Macedonia","alpha-2":"MK","alpha-3":"MKD","country-code":"807","iso_3166-2":"ISO 3166-2:MK","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Northern Mariana Islands","alpha-2":"MP","alpha-3":"MNP","country-code":"580","iso_3166-2":"ISO 3166-2:MP","region":"Oceania","sub-region":"Micronesia","intermediate-region":"","region-code":"009","sub-region-code":"057","intermediate-region-code":""},{"name":"Norway","alpha-2":"NO","alpha-3":"NOR","country-code":"578","iso_3166-2":"ISO 3166-2:NO","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"Oman","alpha-2":"OM","alpha-3":"OMN","country-code":"512","iso_3166-2":"ISO 3166-2:OM","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Pakistan","alpha-2":"PK","alpha-3":"PAK","country-code":"586","iso_3166-2":"ISO 3166-2:PK","region":"Asia","sub-region":"Southern Asia","intermediate-region":"","region-code":"142","sub-region-code":"034","intermediate-region-code":""},{"name":"Palau","alpha-2":"PW","alpha-3":"PLW","country-code":"585","iso_3166-2":"ISO 3166-2:PW","region":"Oceania","sub-region":"Micronesia","intermediate-region":"","region-code":"009","sub-region-code":"057","intermediate-region-code":""},{"name":"Palestine, State of","alpha-2":"PS","alpha-3":"PSE","country-code":"275","iso_3166-2":"ISO 3166-2:PS","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Panama","alpha-2":"PA","alpha-3":"PAN","country-code":"591","iso_3166-2":"ISO 3166-2:PA","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Central America","region-code":"019","sub-region-code":"419","intermediate-region-code":"013"},{"name":"Papua New Guinea","alpha-2":"PG","alpha-3":"PNG","country-code":"598","iso_3166-2":"ISO 3166-2:PG","region":"Oceania","sub-region":"Melanesia","intermediate-region":"","region-code":"009","sub-region-code":"054","intermediate-region-code":""},{"name":"Paraguay","alpha-2":"PY","alpha-3":"PRY","country-code":"600","iso_3166-2":"ISO 3166-2:PY","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Peru","alpha-2":"PE","alpha-3":"PER","country-code":"604","iso_3166-2":"ISO 3166-2:PE","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Philippines","alpha-2":"PH","alpha-3":"PHL","country-code":"608","iso_3166-2":"ISO 3166-2:PH","region":"Asia","sub-region":"South-eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"035","intermediate-region-code":""},{"name":"Pitcairn","alpha-2":"PN","alpha-3":"PCN","country-code":"612","iso_3166-2":"ISO 3166-2:PN","region":"Oceania","sub-region":"Polynesia","intermediate-region":"","region-code":"009","sub-region-code":"061","intermediate-region-code":""},{"name":"Poland","alpha-2":"PL","alpha-3":"POL","country-code":"616","iso_3166-2":"ISO 3166-2:PL","region":"Europe","sub-region":"Eastern Europe","intermediate-region":"","region-code":"150","sub-region-code":"151","intermediate-region-code":""},{"name":"Portugal","alpha-2":"PT","alpha-3":"PRT","country-code":"620","iso_3166-2":"ISO 3166-2:PT","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Puerto Rico","alpha-2":"PR","alpha-3":"PRI","country-code":"630","iso_3166-2":"ISO 3166-2:PR","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Qatar","alpha-2":"QA","alpha-3":"QAT","country-code":"634","iso_3166-2":"ISO 3166-2:QA","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Réunion","alpha-2":"RE","alpha-3":"REU","country-code":"638","iso_3166-2":"ISO 3166-2:RE","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Romania","alpha-2":"RO","alpha-3":"ROU","country-code":"642","iso_3166-2":"ISO 3166-2:RO","region":"Europe","sub-region":"Eastern Europe","intermediate-region":"","region-code":"150","sub-region-code":"151","intermediate-region-code":""},{"name":"Russian Federation","alpha-2":"RU","alpha-3":"RUS","country-code":"643","iso_3166-2":"ISO 3166-2:RU","region":"Europe","sub-region":"Eastern Europe","intermediate-region":"","region-code":"150","sub-region-code":"151","intermediate-region-code":""},{"name":"Rwanda","alpha-2":"RW","alpha-3":"RWA","country-code":"646","iso_3166-2":"ISO 3166-2:RW","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Saint Barthélemy","alpha-2":"BL","alpha-3":"BLM","country-code":"652","iso_3166-2":"ISO 3166-2:BL","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Saint Helena, Ascension and Tristan da Cunha","alpha-2":"SH","alpha-3":"SHN","country-code":"654","iso_3166-2":"ISO 3166-2:SH","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Saint Kitts and Nevis","alpha-2":"KN","alpha-3":"KNA","country-code":"659","iso_3166-2":"ISO 3166-2:KN","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Saint Lucia","alpha-2":"LC","alpha-3":"LCA","country-code":"662","iso_3166-2":"ISO 3166-2:LC","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Saint Martin (French part)","alpha-2":"MF","alpha-3":"MAF","country-code":"663","iso_3166-2":"ISO 3166-2:MF","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Saint Pierre and Miquelon","alpha-2":"PM","alpha-3":"SPM","country-code":"666","iso_3166-2":"ISO 3166-2:PM","region":"Americas","sub-region":"Northern America","intermediate-region":"","region-code":"019","sub-region-code":"021","intermediate-region-code":""},{"name":"Saint Vincent and the Grenadines","alpha-2":"VC","alpha-3":"VCT","country-code":"670","iso_3166-2":"ISO 3166-2:VC","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Samoa","alpha-2":"WS","alpha-3":"WSM","country-code":"882","iso_3166-2":"ISO 3166-2:WS","region":"Oceania","sub-region":"Polynesia","intermediate-region":"","region-code":"009","sub-region-code":"061","intermediate-region-code":""},{"name":"San Marino","alpha-2":"SM","alpha-3":"SMR","country-code":"674","iso_3166-2":"ISO 3166-2:SM","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Sao Tome and Principe","alpha-2":"ST","alpha-3":"STP","country-code":"678","iso_3166-2":"ISO 3166-2:ST","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Middle Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"017"},{"name":"Saudi Arabia","alpha-2":"SA","alpha-3":"SAU","country-code":"682","iso_3166-2":"ISO 3166-2:SA","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Senegal","alpha-2":"SN","alpha-3":"SEN","country-code":"686","iso_3166-2":"ISO 3166-2:SN","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Serbia","alpha-2":"RS","alpha-3":"SRB","country-code":"688","iso_3166-2":"ISO 3166-2:RS","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Seychelles","alpha-2":"SC","alpha-3":"SYC","country-code":"690","iso_3166-2":"ISO 3166-2:SC","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Sierra Leone","alpha-2":"SL","alpha-3":"SLE","country-code":"694","iso_3166-2":"ISO 3166-2:SL","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Singapore","alpha-2":"SG","alpha-3":"SGP","country-code":"702","iso_3166-2":"ISO 3166-2:SG","region":"Asia","sub-region":"South-eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"035","intermediate-region-code":""},{"name":"Sint Maarten (Dutch part)","alpha-2":"SX","alpha-3":"SXM","country-code":"534","iso_3166-2":"ISO 3166-2:SX","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Slovakia","alpha-2":"SK","alpha-3":"SVK","country-code":"703","iso_3166-2":"ISO 3166-2:SK","region":"Europe","sub-region":"Eastern Europe","intermediate-region":"","region-code":"150","sub-region-code":"151","intermediate-region-code":""},{"name":"Slovenia","alpha-2":"SI","alpha-3":"SVN","country-code":"705","iso_3166-2":"ISO 3166-2:SI","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Solomon Islands","alpha-2":"SB","alpha-3":"SLB","country-code":"090","iso_3166-2":"ISO 3166-2:SB","region":"Oceania","sub-region":"Melanesia","intermediate-region":"","region-code":"009","sub-region-code":"054","intermediate-region-code":""},{"name":"Somalia","alpha-2":"SO","alpha-3":"SOM","country-code":"706","iso_3166-2":"ISO 3166-2:SO","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"South Africa","alpha-2":"ZA","alpha-3":"ZAF","country-code":"710","iso_3166-2":"ISO 3166-2:ZA","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Southern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"018"},{"name":"South Georgia and the South Sandwich Islands","alpha-2":"GS","alpha-3":"SGS","country-code":"239","iso_3166-2":"ISO 3166-2:GS","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"South Sudan","alpha-2":"SS","alpha-3":"SSD","country-code":"728","iso_3166-2":"ISO 3166-2:SS","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Spain","alpha-2":"ES","alpha-3":"ESP","country-code":"724","iso_3166-2":"ISO 3166-2:ES","region":"Europe","sub-region":"Southern Europe","intermediate-region":"","region-code":"150","sub-region-code":"039","intermediate-region-code":""},{"name":"Sri Lanka","alpha-2":"LK","alpha-3":"LKA","country-code":"144","iso_3166-2":"ISO 3166-2:LK","region":"Asia","sub-region":"Southern Asia","intermediate-region":"","region-code":"142","sub-region-code":"034","intermediate-region-code":""},{"name":"Sudan","alpha-2":"SD","alpha-3":"SDN","country-code":"729","iso_3166-2":"ISO 3166-2:SD","region":"Africa","sub-region":"Northern Africa","intermediate-region":"","region-code":"002","sub-region-code":"015","intermediate-region-code":""},{"name":"Suriname","alpha-2":"SR","alpha-3":"SUR","country-code":"740","iso_3166-2":"ISO 3166-2:SR","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Svalbard and Jan Mayen","alpha-2":"SJ","alpha-3":"SJM","country-code":"744","iso_3166-2":"ISO 3166-2:SJ","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"Sweden","alpha-2":"SE","alpha-3":"SWE","country-code":"752","iso_3166-2":"ISO 3166-2:SE","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"Switzerland","alpha-2":"CH","alpha-3":"CHE","country-code":"756","iso_3166-2":"ISO 3166-2:CH","region":"Europe","sub-region":"Western Europe","intermediate-region":"","region-code":"150","sub-region-code":"155","intermediate-region-code":""},{"name":"Syrian Arab Republic","alpha-2":"SY","alpha-3":"SYR","country-code":"760","iso_3166-2":"ISO 3166-2:SY","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Taiwan, Province of China","alpha-2":"TW","alpha-3":"TWN","country-code":"158","iso_3166-2":"ISO 3166-2:TW","region":"Asia","sub-region":"Eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"030","intermediate-region-code":""},{"name":"Tajikistan","alpha-2":"TJ","alpha-3":"TJK","country-code":"762","iso_3166-2":"ISO 3166-2:TJ","region":"Asia","sub-region":"Central Asia","intermediate-region":"","region-code":"142","sub-region-code":"143","intermediate-region-code":""},{"name":"Tanzania, United Republic of","alpha-2":"TZ","alpha-3":"TZA","country-code":"834","iso_3166-2":"ISO 3166-2:TZ","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Thailand","alpha-2":"TH","alpha-3":"THA","country-code":"764","iso_3166-2":"ISO 3166-2:TH","region":"Asia","sub-region":"South-eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"035","intermediate-region-code":""},{"name":"Timor-Leste","alpha-2":"TL","alpha-3":"TLS","country-code":"626","iso_3166-2":"ISO 3166-2:TL","region":"Asia","sub-region":"South-eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"035","intermediate-region-code":""},{"name":"Togo","alpha-2":"TG","alpha-3":"TGO","country-code":"768","iso_3166-2":"ISO 3166-2:TG","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Western Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"011"},{"name":"Tokelau","alpha-2":"TK","alpha-3":"TKL","country-code":"772","iso_3166-2":"ISO 3166-2:TK","region":"Oceania","sub-region":"Polynesia","intermediate-region":"","region-code":"009","sub-region-code":"061","intermediate-region-code":""},{"name":"Tonga","alpha-2":"TO","alpha-3":"TON","country-code":"776","iso_3166-2":"ISO 3166-2:TO","region":"Oceania","sub-region":"Polynesia","intermediate-region":"","region-code":"009","sub-region-code":"061","intermediate-region-code":""},{"name":"Trinidad and Tobago","alpha-2":"TT","alpha-3":"TTO","country-code":"780","iso_3166-2":"ISO 3166-2:TT","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Tunisia","alpha-2":"TN","alpha-3":"TUN","country-code":"788","iso_3166-2":"ISO 3166-2:TN","region":"Africa","sub-region":"Northern Africa","intermediate-region":"","region-code":"002","sub-region-code":"015","intermediate-region-code":""},{"name":"Turkey","alpha-2":"TR","alpha-3":"TUR","country-code":"792","iso_3166-2":"ISO 3166-2:TR","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Turkmenistan","alpha-2":"TM","alpha-3":"TKM","country-code":"795","iso_3166-2":"ISO 3166-2:TM","region":"Asia","sub-region":"Central Asia","intermediate-region":"","region-code":"142","sub-region-code":"143","intermediate-region-code":""},{"name":"Turks and Caicos Islands","alpha-2":"TC","alpha-3":"TCA","country-code":"796","iso_3166-2":"ISO 3166-2:TC","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Tuvalu","alpha-2":"TV","alpha-3":"TUV","country-code":"798","iso_3166-2":"ISO 3166-2:TV","region":"Oceania","sub-region":"Polynesia","intermediate-region":"","region-code":"009","sub-region-code":"061","intermediate-region-code":""},{"name":"Uganda","alpha-2":"UG","alpha-3":"UGA","country-code":"800","iso_3166-2":"ISO 3166-2:UG","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Ukraine","alpha-2":"UA","alpha-3":"UKR","country-code":"804","iso_3166-2":"ISO 3166-2:UA","region":"Europe","sub-region":"Eastern Europe","intermediate-region":"","region-code":"150","sub-region-code":"151","intermediate-region-code":""},{"name":"United Arab Emirates","alpha-2":"AE","alpha-3":"ARE","country-code":"784","iso_3166-2":"ISO 3166-2:AE","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"United Kingdom of Great Britain and Northern Ireland","alpha-2":"GB","alpha-3":"GBR","country-code":"826","iso_3166-2":"ISO 3166-2:GB","region":"Europe","sub-region":"Northern Europe","intermediate-region":"","region-code":"150","sub-region-code":"154","intermediate-region-code":""},{"name":"United States of America","alpha-2":"US","alpha-3":"USA","country-code":"840","iso_3166-2":"ISO 3166-2:US","region":"Americas","sub-region":"Northern America","intermediate-region":"","region-code":"019","sub-region-code":"021","intermediate-region-code":""},{"name":"United States Minor Outlying Islands","alpha-2":"UM","alpha-3":"UMI","country-code":"581","iso_3166-2":"ISO 3166-2:UM","region":"Oceania","sub-region":"Micronesia","intermediate-region":"","region-code":"009","sub-region-code":"057","intermediate-region-code":""},{"name":"Uruguay","alpha-2":"UY","alpha-3":"URY","country-code":"858","iso_3166-2":"ISO 3166-2:UY","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Uzbekistan","alpha-2":"UZ","alpha-3":"UZB","country-code":"860","iso_3166-2":"ISO 3166-2:UZ","region":"Asia","sub-region":"Central Asia","intermediate-region":"","region-code":"142","sub-region-code":"143","intermediate-region-code":""},{"name":"Vanuatu","alpha-2":"VU","alpha-3":"VUT","country-code":"548","iso_3166-2":"ISO 3166-2:VU","region":"Oceania","sub-region":"Melanesia","intermediate-region":"","region-code":"009","sub-region-code":"054","intermediate-region-code":""},{"name":"Venezuela (Bolivarian Republic of)","alpha-2":"VE","alpha-3":"VEN","country-code":"862","iso_3166-2":"ISO 3166-2:VE","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"South America","region-code":"019","sub-region-code":"419","intermediate-region-code":"005"},{"name":"Viet Nam","alpha-2":"VN","alpha-3":"VNM","country-code":"704","iso_3166-2":"ISO 3166-2:VN","region":"Asia","sub-region":"South-eastern Asia","intermediate-region":"","region-code":"142","sub-region-code":"035","intermediate-region-code":""},{"name":"Virgin Islands (British)","alpha-2":"VG","alpha-3":"VGB","country-code":"092","iso_3166-2":"ISO 3166-2:VG","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Virgin Islands (U.S.)","alpha-2":"VI","alpha-3":"VIR","country-code":"850","iso_3166-2":"ISO 3166-2:VI","region":"Americas","sub-region":"Latin America and the Caribbean","intermediate-region":"Caribbean","region-code":"019","sub-region-code":"419","intermediate-region-code":"029"},{"name":"Wallis and Futuna","alpha-2":"WF","alpha-3":"WLF","country-code":"876","iso_3166-2":"ISO 3166-2:WF","region":"Oceania","sub-region":"Polynesia","intermediate-region":"","region-code":"009","sub-region-code":"061","intermediate-region-code":""},{"name":"Western Sahara","alpha-2":"EH","alpha-3":"ESH","country-code":"732","iso_3166-2":"ISO 3166-2:EH","region":"Africa","sub-region":"Northern Africa","intermediate-region":"","region-code":"002","sub-region-code":"015","intermediate-region-code":""},{"name":"Yemen","alpha-2":"YE","alpha-3":"YEM","country-code":"887","iso_3166-2":"ISO 3166-2:YE","region":"Asia","sub-region":"Western Asia","intermediate-region":"","region-code":"142","sub-region-code":"145","intermediate-region-code":""},{"name":"Zambia","alpha-2":"ZM","alpha-3":"ZMB","country-code":"894","iso_3166-2":"ISO 3166-2:ZM","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"},{"name":"Zimbabwe","alpha-2":"ZW","alpha-3":"ZWE","country-code":"716","iso_3166-2":"ISO 3166-2:ZW","region":"Africa","sub-region":"Sub-Saharan Africa","intermediate-region":"Eastern Africa","region-code":"002","sub-region-code":"202","intermediate-region-code":"014"}]

    """### a"""

    #Ship_Address_Detail_df = pd.DataFrame(states_code).rename(columns={"name":"Ship_Address_State_Name","alpha-2":"Ship_Address_Postal_State"})
    #Ship_Address_Detail_df = Ship_Address_Detail_df[["Ship_Address_State_Name","Ship_Address_Postal_State"]]
    #Ship_Address_Detail_df

    #df = df.merge(Ship_Address_Detail_df, on="Ship_Address_Postal_State", how="left")
    #df

    country_codes_df = pd.DataFrame(Country_codes, columns=["name", "dial_code", "code"]).rename(columns={"name":"Ship_Address_Country_Name","code":"Ship_Address_Country"})
    country_codes_df

    df = df.merge(country_codes_df, on="Ship_Address_Country", how="left")

    df[["Ship_Address_Country","Ship_Address_Country_Name"]].drop_duplicates()

    """# SQL"""

    import mysql.connector

    from sqlalchemy import create_engine

    # Replace the placeholders with your actual database connection details
    host = 'database-solanoteam.crztpf1c2nue.us-east-1.rds.amazonaws.com'
    port = 3409
    user = 'admin'
    password = '394462ydmu1dC4nVNg1L'
    database = 'ordenes'

    # Create the SQLAlchemy engine
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}')

    # Write the DataFrame to the SQL database
    df.to_sql(name='ordenes_db', con=engine, if_exists='replace', index=False)

    # Dispose of the engine
    engine.dispose()


    show_success_message()
except:
    messagebox.showinfo("Fallo", f"Error al ejecutar")