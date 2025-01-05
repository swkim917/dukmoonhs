import datetime
import streamlit as st
import pandas as pd
from sqlalchemy import text


if "page_name" not in st.session_state:
    st.session_state.page_name = "Devices Info"

if "message" not in st.session_state:
    st.session_state.message = None

# Create the SQL connection to dmgh_db as specified in your secrets file.
conn = st.connection('dmgh_db', type='sql')


def devices_info():
    st.title("기기정보 목록")
    
    if st.session_state.message == "success delete":
        st.session_state.message = None
        st.success("삭제가 성공했습니다!", icon="✅")
        st.balloons()
    
    
    cols = st.columns(4)
    with cols[0]:
        if st.button("새 기기정보 등록", use_container_width=True):
            st.session_state.page_name = "Register Device"
            st.rerun()

    sql = "SELECT UniqueNumber, DeviceType, DeviceStatus, CurrentOwnerEmail, CurrentOwnerName, CurrentOwnerType \
            FROM devices \
            ORDER BY UniqueNumber"
    df_devices = conn.query(sql, ttl=0)

    df_state = st.dataframe(
        df_devices, 
        column_config={
            "UniqueNumber": "고유번호", "DeviceType": "기기 유형", "DeviceStatus": "기기 대여 상태",
            "CurrentOwnerEmail": "현재 소유자 이메일", "CurrentOwnerName": "현재 소유자 이름", "CurrentOwnerType": "현재 소유자 유형 구분"
        },
        on_select="rerun",
        selection_mode="single-row"
    )

    if len(df_state.selection['rows']) > 0:
        # st.write(df_state.selection)
        row_index = df_state.selection['rows'][0]
        # st.write(row_index)
        # st.write(df_devices.iloc[row_index]['UniqueNumber'])
        unique_number = df_devices.iloc[row_index]['UniqueNumber']
        
        st.session_state.unique_number = unique_number
        st.session_state.page_name = "Device Detail"
        st.rerun()



def device_detail():
    st.title("기기정보 상세")
    
    unique_number = st.session_state.unique_number
    
    if st.session_state.message == "success modify":
        st.session_state.message = None
        st.success("수정이 성공했습니다!", icon="✅")
        st.balloons()
    
    if st.session_state.message == "success insert":
        st.session_state.message = None
        st.success("등록이 성공했습니다!", icon="✅")
        st.balloons()
    
    
    cols = st.columns(4)
    with cols[0]:
        if st.button("목록", use_container_width=True):
            st.session_state.page_name = "Devices Info"
            st.session_state.unique_number = None
            st.rerun()
    
    with cols[1]:
        if st.button("삭제", use_container_width=True):
            remove_device(unique_number)
    
    with cols[2]:
        if st.button("수정", use_container_width=True):
            st.session_state.page_name = "Modify Device"
            st.rerun()
    
    
    sql = "SELECT UniqueNumber, SerialNumber, DeviceType, Model, DeviceStatus, StatusNotes, Components, \
            PreviousOwnerEmail, PreviousOwnerName, PreviousOwnerPhoneNumber, \
            CurrentOwnerEmail, CurrentOwnerName, CurrentOwnerPhoneNumber, \
            CurrentOwnerType, RentalStartDate, RentalEndDate, Agree \
            FROM devices \
            WHERE UniqueNumber = :UniqueNumber"
    df_device = conn.query(sql, ttl=0, params={"UniqueNumber": unique_number})
    st.dataframe(df_device)
    
    st.text_input("고유번호", value=df_device.iloc[0]['UniqueNumber'], disabled=True)
    st.text_input("일련번호", value=df_device.iloc[0]['SerialNumber'], disabled=True, max_chars=14)
    
    device_type = df_device.iloc[0]['DeviceType']
    tup = ("태블릿", "노트북")
    index = tup.index(device_type) if device_type else None
    st.selectbox("기기 유형", tup, index=index, disabled=True)
    
    model = df_device.iloc[0]['Model']
    tup = ("Surface Go 3", "")
    index = tup.index(model) if model else None
    st.selectbox("모델명", tup, index=index, disabled=True)
    
    device_status = df_device.iloc[0]['DeviceStatus']
    tup = ("대여 중", "대여 가능", "반납(준비 중)", "사용 불가(수리 중)")
    index = tup.index(device_status) if device_status else None
    st.selectbox("기기 대여 상태", tup, index=index, disabled=True)
    
    st.text_area("기기의 현재 상태에 대한 참고사항", value=df_device.iloc[0]['StatusNotes'], disabled=True)
    
    components = df_device.iloc[0]['Components']
    components = components.strip("[""]").replace('"', '').split(',') if components else None
    st.multiselect("대여한 스마트 기기 구성품", options=["본체", "키보드", "펜", "충전기", "북커버", "박스"], default=components, disabled=True)
    
    st.text_input("이전 소유자 이메일", value=df_device.iloc[0]['PreviousOwnerEmail'], disabled=True)
    st.text_input("이전 소유자 이름", value=df_device.iloc[0]['PreviousOwnerName'], disabled=True)
    st.text_input("이전 소유자 전화번호", value=df_device.iloc[0]['PreviousOwnerPhoneNumber'], disabled=True)
    st.text_input("현재 소유자 이메일", value=df_device.iloc[0]['CurrentOwnerEmail'], disabled=True)
    st.text_input("현재 소유자 이름", value=df_device.iloc[0]['CurrentOwnerName'], disabled=True)
    st.text_input("현재 소유자 전화번호", value=df_device.iloc[0]['CurrentOwnerPhoneNumber'], disabled=True)
    
    current_owner_type = df_device.iloc[0]['CurrentOwnerType']
    tup = ("학생", "교직원")
    index = tup.index(current_owner_type) if current_owner_type else None
    st.selectbox("현재 소유자 유형 구분", tup, index=index, disabled=True)
    
    rental_start_date = df_device.iloc[0]['RentalStartDate']
    date_value = None
    if rental_start_date:
        year, month, day = map(int, rental_start_date.split('-'))
        date_value = datetime.date(year, month, day)
    st.date_input("대여 시작일", value=date_value, disabled=True)
    
    rental_end_date = df_device.iloc[0]['RentalEndDate']
    date_value = None
    if rental_end_date:
        year, month, day = map(int, rental_end_date.split('-'))
        date_value = datetime.date(year, month, day)
    st.date_input("대여 종료일 (기기 반납일)", value=date_value, disabled=True)
    
    agree = df_device.iloc[0]['Agree']
    tup = ("동의함", "동의하지 않음")
    index = tup.index(agree) if agree else None
    st.selectbox("학교 스마트 기기 관리 규정 동의 여부", tup, index=index, disabled=True)



def modify_device():
    st.title("기기정보 수정")
    
    cols = st.columns(4)
    with cols[0]:
        if st.button("취소", use_container_width=True):
            st.session_state.page_name = "Device Detail"
            st.rerun()
    
    unique_number = st.session_state.unique_number
    
    sql = "SELECT UniqueNumber, SerialNumber, DeviceType, Model, DeviceStatus, StatusNotes, Components, \
            PreviousOwnerEmail, PreviousOwnerName, PreviousOwnerPhoneNumber, \
            CurrentOwnerEmail, CurrentOwnerName, CurrentOwnerPhoneNumber, \
            CurrentOwnerType, RentalStartDate, RentalEndDate, Agree \
            FROM devices \
            WHERE UniqueNumber = :UniqueNumber"
    df_device = conn.query(sql, ttl=0, params={"UniqueNumber": unique_number})
    st.dataframe(df_device)
    
    with st.form(key="modify_form"):
        input_unique_number = st.text_input("고유번호", value=df_device.iloc[0]['UniqueNumber'], disabled=True)
        input_serial_number = st.text_input("일련번호", value=df_device.iloc[0]['SerialNumber'], max_chars=14)
        
        device_type = df_device.iloc[0]['DeviceType']
        tup = ("태블릿", "노트북")
        index = tup.index(device_type) if device_type else None
        input_device_type = st.selectbox("기기 유형", tup, index=index)
        
        model = df_device.iloc[0]['Model']
        tup = ("Surface Go 3", "")
        index = tup.index(model) if model else None
        input_model = st.selectbox("모델명", tup, index=index)
        
        device_status = df_device.iloc[0]['DeviceStatus']
        tup = ("대여 중", "대여 가능", "반납(준비 중)", "사용 불가(수리 중)")
        index = tup.index(device_status) if device_status else None
        input_device_status = st.selectbox("기기 대여 상태", tup, index=index)
        
        input_status_notes = st.text_area("기기의 현재 상태에 대한 참고사항", value=df_device.iloc[0]['StatusNotes'])
        
        components = df_device.iloc[0]['Components']
        components = components.strip("[""]").replace('"', '').split(',') if components else None
        input_components = st.multiselect("대여한 스마트 기기 구성품", options=["본체", "키보드", "펜", "충전기", "북커버", "박스"], default=components)
        input_components = '[' + ','.join(input_components) + ']' if len(input_components) > 0 else ''
        
        input_previous_owner_email = st.text_input("이전 소유자 이메일", value=df_device.iloc[0]['PreviousOwnerEmail'])
        input_previous_owner_name = st.text_input("이전 소유자 이름", value=df_device.iloc[0]['PreviousOwnerName'])
        input_previous_owner_phone_number = st.text_input("이전 소유자 전화번호", value=df_device.iloc[0]['PreviousOwnerPhoneNumber'])
        input_current_owner_email = st.text_input("현재 소유자 이메일", value=df_device.iloc[0]['CurrentOwnerEmail'])
        input_current_owner_name = st.text_input("현재 소유자 이름", value=df_device.iloc[0]['CurrentOwnerName'])
        input_current_owner_phone_number = st.text_input("현재 소유자 전화번호", value=df_device.iloc[0]['CurrentOwnerPhoneNumber'])
        
        current_owner_type = df_device.iloc[0]['CurrentOwnerType']
        tup = ("학생", "교직원")
        index = tup.index(current_owner_type) if current_owner_type else None
        input_current_owner_type = st.selectbox("현재 소유자 유형 구분", tup, index=index)
        
        rental_start_date = df_device.iloc[0]['RentalStartDate']
        date_value = None
        if rental_start_date:
            year, month, day = map(int, rental_start_date.split('-'))
            date_value = datetime.date(year, month, day)
        input_rental_start_date = st.date_input("대여 시작일", value=date_value)
        
        rental_end_date = df_device.iloc[0]['RentalEndDate']
        date_value = None
        if rental_end_date:
            year, month, day = map(int, rental_end_date.split('-'))
            date_value = datetime.date(year, month, day)
        input_rental_end_date = st.date_input("대여 종료일 (기기 반납일)", value=date_value)
        
        agree = df_device.iloc[0]['Agree']
        tup = ("동의함", "동의하지 않음")
        index = tup.index(agree) if agree else None
        input_agree = st.selectbox("학교 스마트 기기 관리 규정 동의 여부", tup, index=index)
        
        submit_button = st.form_submit_button(label="수정")
    
    if submit_button:
        # Update some data with conn.session.
        with conn.session as s:
            sql = text("UPDATE devices \
                        SET UniqueNumber = :UniqueNumber, SerialNumber = :SerialNumber, DeviceType = :DeviceType, Model = :Model, \
                            DeviceStatus = :DeviceStatus, StatusNotes = :StatusNotes, Components = :Components, \
                            PreviousOwnerEmail = :PreviousOwnerEmail, PreviousOwnerName = :PreviousOwnerName, PreviousOwnerPhoneNumber = :PreviousOwnerPhoneNumber, \
                            CurrentOwnerEmail = :CurrentOwnerEmail, CurrentOwnerName = :CurrentOwnerName, CurrentOwnerPhoneNumber = :CurrentOwnerPhoneNumber, \
                            CurrentOwnerType = :CurrentOwnerType, RentalStartDate = :RentalStartDate, RentalEndDate = :RentalEndDate, Agree = :Agree \
                        WHERE UniqueNumber = :UniqueNumber")
            s.execute(
                sql,
                {
                    "UniqueNumber": input_unique_number, 
                    "SerialNumber": input_serial_number, 
                    "DeviceType": input_device_type, 
                    "Model": input_model, 
                    "DeviceStatus": input_device_status, 
                    "StatusNotes": input_status_notes, 
                    "Components": input_components,
                    "PreviousOwnerEmail": input_previous_owner_email, 
                    "PreviousOwnerName": input_previous_owner_name, 
                    "PreviousOwnerPhoneNumber": input_previous_owner_phone_number, 
                    "CurrentOwnerEmail": input_current_owner_email, 
                    "CurrentOwnerName": input_current_owner_name, 
                    "CurrentOwnerPhoneNumber": input_current_owner_phone_number, 
                    "CurrentOwnerType": input_current_owner_type, 
                    "RentalStartDate": input_rental_start_date, 
                    "RentalEndDate": input_rental_end_date, 
                    "Agree": input_agree
                }
            )
            s.commit()
            
            # 수정 완료 후 기기정보 상세 화면으로 이동
            st.session_state.page_name = "Device Detail"
            st.session_state.message = "success modify"
            st.rerun()



def register_device():
    st.title("새 기기정보 등록")
    
    cols = st.columns(4)
    with cols[0]:
        if st.button("취소", use_container_width=True):
            st.session_state.page_name = "Devices Info"
            st.rerun()
    
    
    if st.session_state.message == "duplicate unique number":
        # st.session_state.message = None
        st.error("고유번호가 이미 존재합니다! 중복되지 않는 고유번호를 입력하세요.")
    
    
    with st.form(key="register_form"):
        input_unique_number = st.text_input("고유번호")
        input_serial_number = st.text_input("일련번호", max_chars=14)
        
        tup = ("태블릿", "노트북")
        input_device_type = st.selectbox("기기 유형", tup, index=None)
        
        tup = ("Surface Go 3", "")
        input_model = st.selectbox("모델명", tup, index=None)
        
        tup = ("대여 중", "대여 가능", "반납(준비 중)", "사용 불가(수리 중)")
        input_device_status = st.selectbox("기기 대여 상태", tup, index=None)
        
        input_status_notes = st.text_area("기기의 현재 상태에 대한 참고사항")
        
        input_components = st.multiselect("대여한 스마트 기기 구성품", options=["본체", "키보드", "펜", "충전기", "북커버", "박스"], default=None)
        input_components = '[' + ','.join(input_components) + ']' if len(input_components) > 0 else ''
        
        input_previous_owner_email = st.text_input("이전 소유자 이메일")
        input_previous_owner_name = st.text_input("이전 소유자 이름")
        input_previous_owner_phone_number = st.text_input("이전 소유자 전화번호")
        input_current_owner_email = st.text_input("현재 소유자 이메일")
        input_current_owner_name = st.text_input("현재 소유자 이름")
        input_current_owner_phone_number = st.text_input("현재 소유자 전화번호")
        
        tup = ("학생", "교직원")
        input_current_owner_type = st.selectbox("현재 소유자 유형 구분", tup, index=None)
        
        input_rental_start_date = st.date_input("대여 시작일")
        input_rental_end_date = st.date_input("대여 종료일 (기기 반납일)")
        
        tup = ("동의함", "동의하지 않음")
        input_agree = st.selectbox("학교 스마트 기기 관리 규정 동의 여부", tup, index=None)
        
        submit_button = st.form_submit_button(label="등록")
    
    
    if st.session_state.message == "duplicate unique number":
        st.session_state.message = None
        st.error("고유번호가 이미 존재합니다! 중복되지 않는 고유번호를 입력하세요.")
    
    
    if submit_button:
        # 고유번호 중복 여부 확인
        df_device = conn.query(
            "SELECT COUNT(UniqueNumber) AS cnt FROM devices WHERE UniqueNumber = :UniqueNumber",
            ttl=0,
            params={"UniqueNumber": input_unique_number})
        
        # 고유번호가 중복될 경우
        if df_device.iloc[0]['cnt'] == 1:
            st.session_state.message = "duplicate unique number"
            st.rerun()
        
        
        # Insert some data with conn.session.
        with conn.session as s:
            sql = text("INSERT INTO devices (UniqueNumber, SerialNumber, DeviceType, Model, DeviceStatus, StatusNotes, Components, PreviousOwnerEmail, PreviousOwnerName, PreviousOwnerPhoneNumber, CurrentOwnerEmail, CurrentOwnerName, CurrentOwnerPhoneNumber, CurrentOwnerType, RentalStartDate, RentalEndDate, Agree) \
                VALUES (:UniqueNumber, :SerialNumber, :DeviceType, :Model, :DeviceStatus, :StatusNotes, :Components, :PreviousOwnerEmail, :PreviousOwnerName, :PreviousOwnerPhoneNumber, :CurrentOwnerEmail, :CurrentOwnerName, :CurrentOwnerPhoneNumber, :CurrentOwnerType, :RentalStartDate, :RentalEndDate, :Agree)")
            
            s.execute(
                sql,
                {
                    "UniqueNumber": input_unique_number, 
                    "SerialNumber": input_serial_number, 
                    "DeviceType": input_device_type, 
                    "Model": input_model, 
                    "DeviceStatus": input_device_status, 
                    "StatusNotes": input_status_notes, 
                    "Components": input_components,
                    "PreviousOwnerEmail": input_previous_owner_email, 
                    "PreviousOwnerName": input_previous_owner_name, 
                    "PreviousOwnerPhoneNumber": input_previous_owner_phone_number, 
                    "CurrentOwnerEmail": input_current_owner_email, 
                    "CurrentOwnerName": input_current_owner_name, 
                    "CurrentOwnerPhoneNumber": input_current_owner_phone_number, 
                    "CurrentOwnerType": input_current_owner_type, 
                    "RentalStartDate": input_rental_start_date, 
                    "RentalEndDate": input_rental_end_date, 
                    "Agree": input_agree
                }
            )
            s.commit()
            
            # 등록 완료 후 기기정보 상세 화면으로 이동
            st.session_state.unique_number = input_unique_number
            st.session_state.page_name = "Device Detail"
            st.session_state.message = "success insert"
            st.rerun()


@st.dialog("삭제")
def remove_device(unique_number):
    st.write(f"고유번호 {unique_number} 항목 글을 정말 삭제하시겠습니까?")
    
    if st.button("삭제"):
        # Delete some data with conn.session.
        with conn.session as s:
            sql = text("DELETE FROM devices WHERE UniqueNumber = :UniqueNumber")
            s.execute(sql, {"UniqueNumber": unique_number})
            s.commit()
        
        st.session_state.page_name = "Devices Info"
        st.session_state.message = "success delete"
        st.rerun()
    
    

page_names_to_funcs = {
    "Devices Info": devices_info,
    "Device Detail": device_detail,
    "Modify Device": modify_device,
    "Register Device": register_device
}
page_name = st.session_state.page_name
page_names_to_funcs[page_name]()

