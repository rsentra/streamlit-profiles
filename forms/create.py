import streamlit as st
import datetime
from models import database  as db
from libs import utils as util 
import pandas as pd

today = datetime.datetime.today()
years_ago_60 = datetime.datetime(today.year-60,1,1)

@st.experimental_dialog("test Me")
def test_form():
    st.write('test')

@st.experimental_dialog("New Entry")
def show_new_form(form_key ):
    col1, col2,col3 = st.columns(3)
   
    with st.form(form_key, border=False,clear_on_submit =True):
        with col1:
            # 이름 입력
            name = st.text_input("이름", "", placeholder="필수", key=form_key+'nm')
           # 최종학력 선택
            education_options = ["학사", "석사", "전문학사","박사", "고졸"]
            education = st.selectbox("최종학력", education_options, key=form_key+'edu')
            
            # 졸업년월 선택
            graduate_date = st.date_input("졸업년월", min_value = years_ago_60, max_value = today, key=form_key+'gra')
                 #소속
            job_type = st.selectbox("소속", ['자사','프리','자사화'], key=form_key+'job')
            
        with col2:
                # 생년월일 입력
            birth_date = st.date_input("생년월일", min_value = years_ago_60, max_value = today, key=form_key+'bir')   
            # 학교명 입력 (반드시 입력해야 함)
            school_name = st.text_input("학교명", "", placeholder="필수", key=form_key+'sch')
            # 기술등급 선택
            tech_options = ["초급", "중급", "고급", "특급"]
            tech_grade = st.selectbox("기술등급", tech_options, key=form_key+'tech')
            kosa = st.checkbox('kosa 유무', key=form_key+'kosa')
        with col3:    
               # 성별 선택
            gender_options = ["남", "여"]
            gender = st.selectbox("성별", gender_options, key=form_key+'gen')
        
            # 학과명 입력 (반드시 입력해야 함)
            department_name = st.text_input("학과명", "", placeholder="필수", key=form_key+'dep')
            team = st.text_input("팀명", key=form_key+'team')
        
             # certi_name, certi_date = input_certificate('tab1_slider'+form_key)
            # certificates = []
            # acquisition_dates = []   
            ini_val = 0
            if st.session_state['certi_count'] > 0:
                ini_val = st.session_state['certi_count']
            
            key_exp = 'tab_slider'+form_key
            with st.expander("자격증 수"):
                values = st.slider("자격증 수",0, 2, ini_val, label_visibility="hidden", key=key_exp)
                i=0
                certificates = []
                acquisition_dates = []   
                while i < values:
                    certificate = st.text_input("자격증명칭", "", key=f'{key_exp}{i}_cert')
                    if certificate:
                        certificates.append(certificate)
                    acquisition_date = st.date_input("취득년월", key=f'{key_exp}{i}_ym',value=None, min_value = years_ago_60, max_value = today)
                    if certificate:
                        acquisition_dates.append(acquisition_date)
                    i += 1
                    print(i, '번 자격증:',certificate, len(certificates))
                    st.session_state['certi_count'] = len(certificates)
                    st.session_state['certi_name'] = certificates
                    st.session_state['certi_date'] = acquisition_dates
            
        left_col, right_col =  st.columns([0.3,0.7])
        submitted = None
        with left_col:
            # submit를 하면 db에 입력하고 자격증 슬라어더를 초기화함
            submitted = st.form_submit_button("Submit", on_click=util.ini_widget, kwargs={'init_name':'certi_count','init_val':0})
            if submitted:
                dic = {}
                dic['name'] = name
                dic['birth_date'] = datetime.datetime.strftime(birth_date,'%Y-%m-%d')
                dic['gender'], dic['education'] = gender, education
                dic['school_name'], dic['department_name'] = school_name, department_name
                dic['graduate_date'] = datetime.datetime.strftime(graduate_date,'%Y-%m-%d')
                dic['tech_grade'], dic['kosa']= tech_grade, kosa
                dic['team'], dic['job_type'] = team, job_type
                 
                if name =='':
                    st.error("이름을 입력하세요.")
                    return False
                #프로필 테이블 입력
                id_no = db.insert_to_table(schema="members",table="profiles",data=dic, get_seq='members.profiles_id_seq')
                print('insert result = ', id_no, 'certi_list: ', st.session_state['certi_name'])
                st.session_state['id_no'] = id_no
                st.session_state['id_name'] = name

                if st.session_state['certi_name']:
                # if st.session_state['certi_count'] > 0:
                    print('certi:: ',st.session_state['certi_count'], '=', st.session_state['certi_name'])
                    # register_certificates(certi_name, certi_date)
                    id_no = st.session_state['id_no'] 
                    dic = {}
                    dic['id'] = [id_no] * len(st.session_state['certi_name'])
                    dic['certi_name'] = st.session_state['certi_name']
                    dic['certi_date'] = st.session_state['certi_date']
                    df_certi = pd.DataFrame(dic)
                    repl_cond = f"id = {id_no}"
                    res = db.insert_df_to_table(df=df_certi,table="members.certificates", mode='replace',repl_cond=repl_cond)
                    if res:
                        st.session_state['certi_name'] = None
                        st.session_state['certi_date'] = None
                     
        with right_col:
            if submitted:
                st.info(f'insert result = {id_no}', icon="ℹ️")
  
    print('end of form')
    st.session_state['form'] = True
    # 경력 입력
    # if st.session_state['id_name']:
    #     upload_careers('tab1_form')
