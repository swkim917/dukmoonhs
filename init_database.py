import streamlit as st
import pandas as pd
from sqlalchemy import text

st.title("DB 준비")

df_devices = pd.read_csv("SmartDevice.csv")
st.dataframe(df_devices)

# Create the SQL connection to dmgh_db as specified in your secrets file.
conn = st.connection('dmgh_db', type='sql')

# Insert some data with conn.session.
with conn.session as s:
    for row in df_devices.itertuples():
        sql = text("INSERT INTO devices (UniqueNumber, SerialNumber, DeviceType, Model, DeviceStatus, StatusNotes, Components, PreviousOwnerEmail, PreviousOwnerName, PreviousOwnerPhoneNumber, CurrentOwnerEmail, CurrentOwnerName, CurrentOwnerPhoneNumber, CurrentOwnerType, RentalStartDate, RentalEndDate, Agree) \
                VALUES (:UniqueNumber, :SerialNumber, :DeviceType, :Model, :DeviceStatus, :StatusNotes, :Components, :PreviousOwnerEmail, :PreviousOwnerName, :PreviousOwnerPhoneNumber, :CurrentOwnerEmail, :CurrentOwnerName, :CurrentOwnerPhoneNumber, :CurrentOwnerType, :RentalStartDate, :RentalEndDate, :Agree)")
        
        s.execute(
            sql,
            {
                "UniqueNumber": str(row[1]).zfill(3), 
                "SerialNumber": row[2], 
                "DeviceType": row[3], 
                "Model": row[4], 
                "DeviceStatus": row[5], 
                "StatusNotes": row[6], 
                "Components": row[8],
                "PreviousOwnerEmail": row[10], 
                "PreviousOwnerName": row[11], 
                "PreviousOwnerPhoneNumber": row[12], 
                "CurrentOwnerEmail": row[14], 
                "CurrentOwnerName": row[15], 
                "CurrentOwnerPhoneNumber": row[16], 
                "CurrentOwnerType": row[17], 
                "RentalStartDate": row[18], 
                "RentalEndDate": row[19], 
                "Agree": row[20]
            }
        )
    s.commit()

st.subheader("완료!")