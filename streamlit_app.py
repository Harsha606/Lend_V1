import streamlit as st
import pandas as pd
import math
from PIL import Image
from streamlit_option_menu import option_menu
import plotly.express as px
from snowflake.snowpark import Session
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
from snowflake.snowpark.functions import avg, sum, col, lit
from config import connection_parameters
st.set_page_config(page_title="LendingAI powered by Snowflake", page_icon="lendingai_logo.png",layout="wide")
st.image('LendingAI.png', width=220)
session=Session.builder.configs(connection_parameters).create()
selected_opt  = option_menu(None, ["Predictor App" ,"Defaulter App","Recommendation App","Segmentation",'Applications Data','Churn Data','Defaulter Data'],  
default_index=0, orientation="horizontal",icons=None,
                menu_icon=None,
                styles={              
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                # "icon": {"color": "orange", "font-size": "25px"},
                "icon":{"display":"none"},
                "nav": {"background-color":"#f2f5f9"},
                "nav-link": {"font-size": "10px",
                "font-weight":"bold",
                "color":"#1d1160",
                "border-right":"2px solid #4B0082",
                "border-left":"1.5px solid #4B0082",
                "border-top":"1.5px solid #4B0082",
                "border-bottom":"1.5px solid #4B0082",
                "padding":"10px",
                "text-transform": "uppercase",
                "border-radius":"1px",
                "margin":"1px",
                "--hover-color": "#e1e1e1"},
                "nav-link-selected": {"background-color":"#1d1160", "color":"#ffffff"},
                })
if selected_opt == 'Predictor App':
    col1, col2=st.columns([3.2,6.8])
    with col1:
            employment_length = st.selectbox('Experience:', ['< 1 year', '1 year', '2 years', '3 years', '4 years', '5 years', '6 years', '7 years', '8 years', '9 years', '10+ years'])
            loan_title = st.selectbox('Type of Loan:', ['Major purchase', 'Debt consolidation', 'Home improvement', 'Moving and relocation', 'Home buying', 'Business', 'Vacation', 'Car financing', 'Medical expenses', 'Credit card refinancing'])
            age = st.selectbox('Age:', ['< 18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+'])
            amount_requested = st.number_input('Loan Amount:', min_value=0,value=1000)
            tenure = st.selectbox('Loan Repayment Tenure:', ['36 Months','60 Months'])
    col111,col112,col113,coll14=st.columns([1.2,0.8,1,7])
    with col112:
            btn=st.button("Predict")
    with col2:
        if btn:
            lst = [624, 61.62, employment_length,loan_title,amount_requested]
            df = pd.DataFrame([lst], columns=['RISK_SCORE','DEBT_TO_INCOME_RATIO','EMPLOYMENT_LENGTH', 'LOAN_TITLE','AMOUNT_REQUESTED'])
            snow_df = session.create_dataframe(df)
            snow_df.write.mode("overwrite").saveAsTable("LENDINGAI_DB.BASE.TBL_APPLICATIONSCORE_VALIDATION_DS_SNOWPARK")
            res = session.call('LENDINGAI_DB.MART.SP_APPLICATIONSCORE_LR_VALIDATIONPROC_SNOWPARK')
            probability_of_approval = math.floor(float(res[18:20] + '.' + res[21]))
            probability_of_rejection = math.ceil(float(res[7:9] + '.' + res[11]))
            fig = px.bar(
                x=['Approved', 'Rejected'],
                y=[probability_of_approval, probability_of_rejection],
                color=['Approved', 'Rejected'],  
                color_discrete_map={'Approved': '#00A300', 'Rejected': '#FF4500'},
                labels={'x': 'Loan', 'y': 'Probability'}
            )
            fig.update_traces(marker_line_color='black', marker_line_width=1,hovertemplate=None)
            for i in range(2):
                fig.add_annotation(
                            x=['Approved', 'Rejected'][i],
                            y=[probability_of_approval, probability_of_rejection][i]+2,
                            text=f'{[probability_of_approval, probability_of_rejection][i]}%',
                            showarrow=False,
                            font=dict(size=14, color='black'),
                            align='center',
                            valign='bottom' if [probability_of_approval, probability_of_rejection][i] > 50 else 'top',
                        )
            st.write("")
            st.markdown("<center><b>Probability of Loan Approval</b></center>",unsafe_allow_html=True)
            st.plotly_chart(fig,use_container_width=True)
if selected_opt =='Defaulter App':
    col1, col2, col3=st.columns([2,4,4])
    with col1:
            loan_amnt = st.number_input('Loan Amount:',value=10000)
            home_ownership = st.selectbox('Home Ownership:',('OWN', 'RENT', 'MORTGAGE','ANY'))
            annual_income = st.number_input('Annual Income:', value=120000)
            loan_type = st.selectbox('Type of Loan:',
            ('Credit card refinancing','Debt consolidation','Home improvement','Major purchase','Business','Medical expenses','Moving and relocation','Vacation','Home buying','Green loan','Car financing','Other'))
            int_rate=st.number_input('Interest Rate:',value=10)
            credit_score=st.number_input('Credit Score:',value=0)
            term = st.radio("Loan Repayment Term:",["36 months", "60 months"],horizontal=True)
            Employee_Expe = ["< 1 year","2 years","3 years","4 years","5 years","6 years","7 years","8 years","9 years","10+ years"]
            emp_lengt = st.select_slider('Experience:', options=Employee_Expe)
    col111,col112,col113,col114=st.columns([0.6,0.8,0.6,8])
    with col112:
            btn=st.button("Check")
    def is_valid_data2(credit_score,loan_amnt,annual_income,int_rate):
        if(0<=credit_score<=900  and loan_amnt>=0 and annual_income>=0 and int_rate>=0):
            return True
        return False  
    if btn:
          if is_valid_data2(credit_score,loan_amnt,annual_income,int_rate):
                if credit_score==0:
                    risk_score=596
                    if int_rate>20:
                        risk_score+=80
                    elif 15<=int_rate<20:
                        risk_score+=60
                    elif 10<=int_rate<15:
                        risk_score+=30
                    elif 5<=int_rate<10:
                        risk_score+=10
                else:
                    risk_score=credit_score
                lst=[emp_lengt,int_rate,float(loan_amnt),term,home_ownership,float(annual_income),loan_type,risk_score]
                df=pd.DataFrame([lst],columns=['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE'])
                snow_df=session.create_dataframe(df)
                snow_df.write.mode("overwrite").saveAsTable("LENDINGAI_DB.BASE.TBL_DEFAULTER_VALIDATION_DS")
                res=session.call('LENDINGAI_DB.MART.SP_DEFAULTER_VALIDATION_PROC')
                probability_of_nondefaulter,probability_of_defaulter=math.floor(float(res[7:9]+'.'+res[11])), math.ceil(float(res[18:20]+'.'+res[21]))
                with col2:
                  fig = px.bar(                                     
                    x=['No', 'Yes'],
                    y=[probability_of_nondefaulter, probability_of_defaulter],
                    color=['No','Yes'],
                    color_discrete_map = {'Yes': '#00A300', 'No': '#FF4500'},
                    labels={'x': 'Defaulter', 'y': 'Probability'})
                  fig.update_traces(marker_line_color='black', marker_line_width=1,hovertemplate=None)
                  for _ in range(6):
                      st.write("")
                  st.markdown("<center><b>{}</b></center>".format("Probability of Customer Defaulter"),unsafe_allow_html=True)
                  st.plotly_chart(fig,use_container_width=True)
                with col3:
                  for _ in range(6):
                      st.write("")
                  st.markdown("<center><b>{}</b></center>".format("Top 5 Features Influencing Prediction"),unsafe_allow_html=True)
                  for _ in range(5):
                      st.write("")
                  st.image("defaulter_feat_imp.png",use_column_width="always")
          else:
            st.error("Entered Invalid data, Please check your Inputs...")
if selected_opt == 'Recommendation App':
    # Get data from Snowflake for the tables
    transform_df = session.sql('SELECT * FROM LENDINGAI_DB.BASE.TBL_ID_TABLE;').collect()
    # Convert Snowflake DataFrames to pandas DataFrames
    trans_id_data = pd.DataFrame(transform_df)
    data=trans_id_data['id'].iloc[:10000]
    col1,col2,col3=st.columns(3)
    with col2:
            # Create the dropdown
            selected_id = st.selectbox("Select Application ID:", data)
            # Define a CSS style for the dropdown
        # Filter the DataFrame based on the selected "ID"
            filtered_df = trans_id_data[trans_id_data['id'] == selected_id]
            # Display "EMP_TITLE" values based on the selected "ID"
    col4, col5, col6 = st.columns(3)
    with col4:
            st.write("")
            st.write("Occupation of Employee:")
            st.success(filtered_df['EMP_TITLE'].values[0])
            # Display "TITLE" values based on the selected "ID"
    with col5:
            st.write("")
            st.write("Current Loan:")
            st.success(filtered_df['TITLE'].values[0])
            # Display "LOAN_AMNT" values based on the selected "ID"
    with col6:
            st.write("")
            st.write("Loan Amount:")
            st.success(filtered_df['LOAN_AMNT'].values[0])
    filtered_titles = filtered_df['TITLE'].tolist()
            #selected_title = col1.selectbox("Select title", filtered_titles)
    INPUT_LIST = [filtered_titles]
    INPUT_PRODUCT= filtered_titles
                #snowflake_array = snowflake_session.to_array(INPUT_PRODUCT)
    snowflake_array=','.join(map(str, INPUT_PRODUCT))
    k=session.call('LENDINGAI_DB.BASE.SP_RECOMMENDER',snowflake_array)
    arr=k.split(',')
    loans=["Business","Medical expenses","Major purchase","Learning and training","Credit card refinancing","Debt consolidation","Car financing","Vacation","Moving and relocation","Green loans","Home improvement","Home buying"]
    loan_images=["business_loan.jpg","medical_expenses_loan.jpg","major_purchase_loan.jpg","learning_loan.jpg","credit_card_refinancing.jpg","debt_consolidation.png","car_financing_loan.png","vacation_loan.png","moving_loan.png","green_loan.jpg","home_improvement.jpg","home_buying_loan.png"]
    imgs=dict(zip(loans,loan_images))
    if len(arr)==2:
        arr[0]=arr[0][:-1]
        arr[1]=arr[1][2:]
        res=arr
        with col5:
            st.write("")
            st.write("Recommended Loan(s):")
        colr1,colr2,colr3,colr4,colr5,colr6=st.columns(6)
        with colr3:
            st.markdown("<center><b>{}</b></center>".format(res[0]),unsafe_allow_html=True)
            st.image(imgs[res[0]])
        with colr4:
            st.markdown("<center><b>{}</b></center>".format(res[1]),unsafe_allow_html=True)
            st.image(imgs[res[1]])
    elif len(arr)==1:
        res=arr
        with col5:
            st.write("")
            st.write("Recommended Loan(s):")
        col11,col12,col13,col14,col15=st.columns(5)
        with col13:
            st.markdown("<center><b>{}</b></center>".format(res[0]),unsafe_allow_html=True)
            st.image(imgs[res[0]])
if selected_opt=='Segmentation':
    #table_name = 'LENDINGAI.SOURCE.TBL_KMEANS'
    #st.dataframe(df)
    # Create a row with three columns
    col1, col2, col3 = st.columns(3)
    # Column 1: Filters
    with col1:
        selected_term = st.selectbox('Term:',["60 months","36 months"] )
        selected_home_ownership = st.selectbox('Home Ownership:', ["RENT","MORTGAGE","ANY","OWN","NONE"])
    with col2:
        annual_income_input = st.number_input('Annual Income:', min_value=0,value=100000)
        loan_amount_input = st.number_input('Loan Amount:', min_value=0,value=10000)
    with col3:
        selected_purpose = st.selectbox('Purpose:', ["house","medical","vacation","moving","credit_card","home_improvement","small_business","major_purchase","car","renewable_energy","wedding","debt_consolidation","educational","other"])
        selected_cluster = st.selectbox('Clusters:', ["All Clusters",0,1,2,3,4])
        #selected_debt_settlement_flag = st.selectbox('Debt Settlement Flag:', distinct_debt_settlement_flag)
    if 1 <= loan_amount_input <= 10000:
        min_value = 1
        max_value = 10000
    elif 10001 <= loan_amount_input <= 20000:
        min_value = 10001
        max_value = 20000
    elif 20001 <= loan_amount_input <= 30000:
        min_value = 20001
        max_value = 30000
    elif 30001 <= loan_amount_input <= 40000:
        min_value = 30001
        max_value = 40000
    else:
        min_value = 40001  # Default to more than 40K
        max_value = 45000  # Set a very large value for the upper limit
    if 0 <= annual_income_input <= 100000:
        min_income = 0
        max_income = 100000
    elif 100001 <= annual_income_input <= 200000:
        min_income = 100001
        max_income = 200000
    elif 200001 <= annual_income_input <= 300000:
        min_income = 200001
        max_income = 300000
    elif 300001 <= annual_income_input <= 400000:
        min_income = 300001
        max_income = 400000
    else:
        min_income = 400001  # Default to more than 4L
        max_income = 600000  # Set a very large value for the upper limit
    col11,col12,col13,col14,col15,col16,col17,col18,col19=st.columns(9)
    with col15:
      btnn=st.button("Submit")
    # Create a button to apply the filter
    if btnn:
        table_name = session.sql('SELECT * FROM LENDINGAI_DB.MART.TBL_KMEANS_SEGMENTATION2').collect()
        df = pd.DataFrame(table_name)
        df['ANNUAL_INC']=pd.to_numeric(df['ANNUAL_INC'], errors='coerce')
        df=df.dropna(subset=['ANNUAL_INC'])
        condition1 = df['TERM']==selected_term
        condition2 = (min_value <= df['LOAN_AMNT']) & (df['LOAN_AMNT'] <= max_value)
        condition3 = (min_income <= df['ANNUAL_INC']) & (df['ANNUAL_INC'] <= max_income)
        condition4 = df['PURPOSE']==selected_purpose
        condition5 =  df['HOME_OWNERSHIP']==selected_home_ownership
        condition6 = df['CLUSTERS'] == selected_cluster        
        # Check if the selected filter values are not the default values before creating the query
        if selected_term != 'Select Term' and selected_home_ownership != 'Select Home Ownership':
            # Create a query based on all selected filters and the loan amount and annual income inputs
            if selected_cluster == "All Clusters":
                # Create a query to select the table data within specified filters
                condition= condition1 & condition2 & condition3 & condition4 & condition5
                df2=df[(condition)].reset_index(drop=True)
                count_result = len(df2)
                st.write(f"Approved Applications: {count_result}")
                st.write("Table Data Based on Filters:")
                st.dataframe(df2)
                df3 = df2.groupby("LOAN_STATUS").size().reset_index(name="Approved Applications")
                col8, col9 = st.columns(2)
                # Create a bar graph with values displayed on top of bars
                with col8:
                    if not df3.empty:
                        # Create a bar chart using Plotly
                        st.write("Approved Applications by Loan Status")
                        fig = px.bar(df3, x="LOAN_STATUS", y="Approved Applications", labels={"LOAN_STATUS": "Loan Status", "Approved Applications": "Approved Applications"})
                        fig.update_layout(
                            xaxis_tickangle=-45  # Rotate x-axis labels for better readability
                        )
                        fig.update_traces(texttemplate='%{y}')  # Add value annotations on top of each bar
                        st.plotly_chart(fig, use_container_width=True)
                with col9:
                    condition= condition1 & condition2 & condition3 & condition4 & condition5
                    df4=df[(condition)].reset_index(drop=True)
                    df5 = df4.groupby("CLUSTERS").size().reset_index(name="Approved Applications")        
                    # Create a pie chart using Plotly without custom colors
                    fig = px.pie(df5, names='CLUSTERS', values='Approved Applications',
                                hover_data=['CLUSTERS', 'Approved Applications'],
                                labels={'CLUSTERS': 'CLUSTER'})
                    # Customize the appearance of the chart
                    fig.update_traces(textinfo='label', textposition='inside', textfont_size=20)
                    # Display the interactive pie chart
                    st.write("Approved Applications by Clusters")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                condition= condition1 & condition2 & condition3 & condition4 & condition5 & condition6
                df2=df[(condition)].reset_index(drop=True)
                count_result = len(df2)
                st.write(f"Approved Applications: {count_result}")
                st.write("Table Data Based on Filters:")
                st.dataframe(df2)
                df3 = df2.groupby("LOAN_STATUS").size().reset_index(name="Approved Applications")
                col8, col9 = st.columns(2)
                # Create a bar graph with values displayed on top of bars
                with col8:
                    if not df3.empty:
                        st.write("Approved Applications by Loan Status")
                        # Create a bar chart using Plotly
                        fig = px.bar(df3, x="LOAN_STATUS", y="Approved Applications", labels={"LOAN_STATUS": "Loan Status", "Approved Applications": "Approved Applications"})
                        fig.update_layout(
                            xaxis_tickangle=-45  # Rotate x-axis labels for better readability
                        )
                        fig.update_traces(texttemplate='%{y}', textposition='outside')  # Add value annotations on top of each bar
                        st.plotly_chart(fig, use_container_width=True)
                # Create a pie chart with values displayed on hove
                with col9:
                    condition= condition1 & condition2 & condition3 & condition4 & condition5
                    df4=df[(condition)].reset_index(drop=True)
                    df5 = df4.groupby("CLUSTERS").size().reset_index(name="Approved Applications")        
                    # Create a pie chart using Plotly without custom colors
                    fig = px.pie(df5, names='CLUSTERS', values='Approved Applications',
                                hover_data=['CLUSTERS', 'Approved Applications'],
                                labels={'CLUSTERS': 'CLUSTER'})
                    # Customize the appearance of the chart
                    fig.update_traces(textinfo='percent+label', textposition='inside', textfont_size=20)
                    st.write("Approved Applications by Clusters")
                    # Display the interactive pie chart
                    st.plotly_chart(fig, use_container_width=True)
if selected_opt == 'Applications Data':
    res = session.call('LENDINGAI_DB.MART.SP_APPLICATIONSCORE_LR_VALIDATIONPROC_SNOWPARK')
    col1, col2 =st.columns([2.8,7.2])
    with col1:
        emp_length = st.selectbox("Experience:", ['< 1 year', '1 year', '2 years', '3 years', '4 years', '5 years', '6 years', '7 years', '8 years', '9 years', '10+ years'], key="emp_length")
        debt_to_income_ratio = st.number_input('DTI Ratio:', min_value=0.0, key="debt_to_income_ratio")
        amount_requested = st.number_input('Loan Amount:', min_value=0, key="amount_requested")
        loan_title = st.selectbox('Type of Loan:', ['Major purchase', 'Debt consolidation', 'Home improvement', 'Moving and relocation', 'Home buying', 'Business', 'Vacation', 'Car financing', 'Medical expenses', 'Credit card refinancing'], key="loan_title")
        application_status = st.selectbox("Select the application status", ['Approved', 'Rejected','Both'], key="application_status")
        age = st.selectbox('Age:', ['0-18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+'])
        tenure = st.selectbox('Loan Repayment Tenure:', ['36 Months','60 Months'])
        risk_score = st.number_input('Credit Score (Optional):', min_value=0, key="risk_score")
    col11,col12,col13,col14=st.columns([0.4,2.0,0.4,7.2])
    with col12:
      btn4=st.button('Retrieve Related Applications',key='button_cntr2')
    # Predict
    if risk_score == 0:  # assuming default value of the input is 0 when nothing is entered
        risk_score = 624
    if debt_to_income_ratio >= 500:
        risk_score += 10
    elif debt_to_income_ratio >= 200:
        risk_score += 20
    elif debt_to_income_ratio >= 100:
        risk_score += 30
    elif debt_to_income_ratio >= 50:
        risk_score += 50
    elif debt_to_income_ratio >= 20:
        risk_score += 60
    elif debt_to_income_ratio >= 10:
        risk_score += 70
    else:
        risk_score += 80
    risk_score += debt_to_income_ratio
    def is_valid_data(risk_score, amount_requested):
        if (0 <= risk_score <= 1000 and amount_requested >= 0):
            return True
        return False
    with col2:
      if not btn4:
        res1 = session.sql('CALL LENDINGAI_DB.BASE.SP_APPLICATIONSCORE_APPLICANTIONS_SNOWPARK()').collect()
        app_df = pd.DataFrame(res1).iloc[:20]
        final_appscore_df = app_df[['RISK_SCORE','DEBT_TO_INCOME_RATIO','EMPLOYMENT_LENGTH','LOAN_TITLE','AMOUNT_REQUESTED']]
        fig2 = go.Figure(data=[go.Table(
                      columnwidth=[2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
                      header=dict(
                          values=["<b>EMPLOYMENT LENGTH</b>", "<b>DEBT TO INCOME RATIO</b>", "<b>AMOUNT REQUESTED</b>", "<b>LOAN TITLE</b>", "<b>CREDIT SCORE</b>"],
                          fill_color='#CDCDD6',
                          font_color="#4C4C54",
                          align=['center'],
                          line_color='#ffffff',
                          font_size=14,
                          height=20
                      ),
                      cells=dict(values=[final_appscore_df.EMPLOYMENT_LENGTH,final_appscore_df.DEBT_TO_INCOME_RATIO,final_appscore_df.AMOUNT_REQUESTED,final_appscore_df.LOAN_TITLE,final_appscore_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                      # Update the layout of the Plotly table
        fig2.update_layout(
                          autosize=False,
                          width=970,
                          height=600,
                          margin=dict(l=0, r=0, b=0, t=0, pad=4),
                          paper_bgcolor="#ffffff"
                      )
        st.subheader("List of Applications")
        st.plotly_chart(fig2)
      if btn4:
          if is_valid_data(risk_score, amount_requested):
              lst = [risk_score, debt_to_income_ratio,emp_length,loan_title,amount_requested]
              df = pd.DataFrame([lst], columns=['RISK_SCORE','DEBT_TO_INCOME_RATIO','EMPLOYMENT_LENGTH','LOAN_TITLE','AMOUNT_REQUESTED'])
              snow_df = session.create_dataframe(df)
              snow_df.write.mode("overwrite").saveAsTable("LENDINGAI_DB.BASE.TBL_APPLICATIONSCORE_APPLICATIONS_SNOWPARK")
              res1 = session.sql('CALL LENDINGAI_DB.BASE.SP_APPLICATIONSCORE_APPLICANTIONS_SNOWPARK()').collect()
              app_df = pd.DataFrame(res1)
          if application_status == "Approved":
                app_df = app_df[app_df['APPLICATION_STATUS'] == 1]
                st.subheader("List of Approved Applications")
          elif application_status == "Rejected":
                app_df = app_df[app_df['APPLICATION_STATUS'] == 0]
                st.subheader("List of Rejected Applications")
          elif application_status == "Both":
                app_df = app_df[(app_df['APPLICATION_STATUS'] == 1) | (app_df['APPLICATION_STATUS'] == 0)]
                st.subheader("List of Both Approved & Rejected Applications")
          final_appscore_df = app_df[['RISK_SCORE','DEBT_TO_INCOME_RATIO','EMPLOYMENT_LENGTH','LOAN_TITLE','AMOUNT_REQUESTED']]
          fig2 = go.Figure(data=[go.Table(
                    columnwidth=[2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
                    header=dict(
                        values=["<b>EMPLOYMENT LENGTH</b>", "<b>DEBT TO INCOME RATIO</b>", "<b>AMOUNT REQUESTED</b>", "<b>LOAN TITLE</b>", "<b>CREDIT SCORE</b>"],
                        fill_color='#CDCDD6',
                        font_color="#4C4C54",
                        align=['center'],
                        line_color='#ffffff',
                        font_size=14,
                        height=20
                    ),
                    cells=dict(values=[final_appscore_df.EMPLOYMENT_LENGTH,final_appscore_df.DEBT_TO_INCOME_RATIO,final_appscore_df.AMOUNT_REQUESTED,final_appscore_df.LOAN_TITLE,final_appscore_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                    # Update the layout of the Plotly table
          fig2.update_layout(
                        autosize=False,
                        width=970,
                        height=600,
                        margin=dict(l=0, r=0, b=0, t=0, pad=4),
                        paper_bgcolor="#ffffff"
                    )
          st.plotly_chart(fig2)
if selected_opt =='Churn Data':
    col1, col2 =st.columns([2.8,7.2])
    with col1:
      loan_amnt = st.number_input('Loan Amount:',value=10000)
      home_ownership = st.selectbox('Type of Home Ownership:',('OWN', 'RENT', 'MORTGAGE','ANY'))
      annual_income = st.number_input('Annual Income:', value=120000)
      loan_type = st.selectbox('Type of Loan:',
      ('Credit card refinancing','Debt consolidation','Home improvement','Major purchase','Business','Medical expenses','Moving and relocation','Vacation','Home buying','Green loan','Car financing','Other'))
      Employee_Exp = ["< 1 year","2 years","3 years","4 years","5 years","6 years","7 years","8 years","9 years","10+ years"]
      int_rate=st.number_input('Interest Rate:',value=10)
      term = st.radio("Loan Repayment Term:",["36 months", "60 months"],horizontal=True)
      emp_length = st.select_slider("Experience:", options=Employee_Exp)
      credit_score=st.number_input('Credit Score (Optional)',value=0)
      appln_type = st.selectbox('Select preferred application data for retrievel:',('Retrieve Churned Applications ','Retrieve Retained Applications','Retrieve Both Applications'))
      btn1=st.button('Get Data',key='button_cntr6')
    def is_valid_data(credit_score,loan_amnt,annual_income,int_rate):
        if(0<=credit_score<=900  and loan_amnt>=0 and annual_income>=0 and int_rate>=0):
            return True
        return False  
    with col2:
      if not btn1:
        res=session.sql('CALL LENDINGAI_DB.BASE.SP_CHURN_APPLICATIONS()').collect()
        churned_df=pd.DataFrame(res).iloc[:20]
        final_churned_df=churned_df[['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE']]
        fig44 = go.Figure(data=[go.Table(
        columnwidth=[2.5, 1.5, 2.5, 2.5, 3.0, 2.5, 2.5],
        header=dict(
                      values=["<b>EMP_LENGTH</b>", "<b>INT_RATE</b>", "<b>LOAN_AMNT</b>", "<b>TERM</b>", "<b>HOME_OWNERSHIP</b>","<b>ANNUAL_INC</b>", "<b>TITLE</b>","<b>CREDIT SCORE</b>"],
                      fill_color='#CDCDD6',
                      font_color="#4C4C54",
                      align=['center'],
                      line_color='#ffffff',
                      font_size=14,
                      height=40
                  ),
                  cells=dict(values=[final_churned_df.EMP_LENGTH,final_churned_df.INT_RATE,final_churned_df.LOAN_AMNT,final_churned_df.TERM,final_churned_df.HOME_OWNERSHIP,final_churned_df.ANNUAL_INC,final_churned_df.TITLE,final_churned_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                  # Update the layout of the Plotly table
        fig44.update_layout(autosize=False,width=970,
                      height=600,
                      margin=dict(l=0, r=0, b=0, t=0, pad=4),
                      paper_bgcolor="#ffffff"
                  )
        st.subheader("List of Applications")
        st.plotly_chart(fig44)
      if btn1:
        if is_valid_data(credit_score,loan_amnt,annual_income,int_rate):
            if credit_score==0:
                risk_score=602
                if int_rate>20:
                    risk_score+=80
                elif 15<=int_rate<20:
                    risk_score+=60
                elif 10<=int_rate<15:
                    risk_score+=30
                elif 5<=int_rate<10:
                    risk_score+=10
            else:
                risk_score=credit_score
            lst=[emp_length,int_rate,float(loan_amnt),term,home_ownership,float(annual_income),loan_type,risk_score]
            df=pd.DataFrame([lst],columns=['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE'])
            snow_df=session.create_dataframe(df)
            snow_df.write.mode("overwrite").saveAsTable("LENDINGAI_DB.BASE.TBL_CHURN_VALIDATION_DS")
            res=session.call('LENDINGAI_DB.MART.SP_CHURN_VALIDATION_PROC')
            churn_or_not=res[1]
            if appln_type=='Retrieve Churned Applications ':
                res=session.sql('CALL LENDINGAI_DB.BASE.SP_CHURN_APPLICATIONS()').collect()
                df=pd.DataFrame(res)
                churned_df=df[df['LOAN_STATUS_BIN']==1]
                final_churned_df=churned_df[['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE']]
                fig2 = go.Figure(data=[go.Table(
                columnwidth=[2.5, 1.5, 2.5, 2.5, 3.0, 2.5, 2.5],
                header=dict(
                    values=["<b>EMP_LENGTH</b>", "<b>INT_RATE</b>", "<b>LOAN_AMNT</b>", "<b>TERM</b>", "<b>HOME_OWNERSHIP</b>","<b>ANNUAL_INC</b>", "<b>TITLE</b>","<b>CREDIT SCORE</b>"],
                    fill_color='#CDCDD6',
                    font_color="#4C4C54",
                    align=['center'],
                    line_color='#ffffff',
                    font_size=14,
                    height=40
                ),
                cells=dict(values=[final_churned_df.EMP_LENGTH,final_churned_df.INT_RATE,final_churned_df.LOAN_AMNT,final_churned_df.TERM,final_churned_df.HOME_OWNERSHIP,final_churned_df.ANNUAL_INC,final_churned_df.TITLE,final_churned_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                # Update the layout of the Plotly table
                fig2.update_layout(
                    autosize=False,
                    width=970,
                    height=600,
                    margin=dict(l=0, r=0, b=0, t=0, pad=4),
                    paper_bgcolor="#ffffff"
                )
                st.subheader("List of Churned Applications")
                st.plotly_chart(fig2)
            elif appln_type == 'Retrieve Retained Applications':
                res=session.sql('CALL LENDINGAI_DB.BASE.SP_CHURN_APPLICATIONS()').collect()
                df=pd.DataFrame(res)
                churned_df=df[df['LOAN_STATUS_BIN']==0]
                final_churned_df=churned_df[['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE']]
                fig3 = go.Figure(data=[go.Table(
                columnwidth=[2.5, 1.5, 2.5, 2.5, 3.0, 2.5, 2.5],
                header=dict(
                    values=["<b>EMP_LENGTH</b>", "<b>INT_RATE</b>", "<b>LOAN_AMNT</b>", "<b>TERM</b>", "<b>HOME_OWNERSHIP</b>","<b>ANNUL_INC</b>", "<b>TITLE</b>","<b>CREDIT SCORE</b>"],
                    fill_color='#CDCDD6',
                    font_color="#4C4C54",
                    align=['center'],
                    line_color='#ffffff',
                    font_size=14,
                    height=40
                ),
                cells=dict(values=[final_churned_df.EMP_LENGTH,final_churned_df.INT_RATE,final_churned_df.LOAN_AMNT,final_churned_df.TERM,final_churned_df.HOME_OWNERSHIP,final_churned_df.ANNUAL_INC,final_churned_df.TITLE,final_churned_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                # Update the layout of the Plotly table
                fig3.update_layout(
                    autosize=False,
                    width=970,
                    height=600,
                    margin=dict(l=0, r=0, b=0, t=0, pad=4),
                    paper_bgcolor="#ffffff"
                )
                st.subheader("List of Retained Applications")
                st.plotly_chart(fig3)
            elif appln_type == 'Retrieve Both Applications':
                res=session.sql('CALL LENDINGAI_DB.BASE.SP_CHURN_APPLICATIONS()').collect()
                churned_df=pd.DataFrame(res)
                final_churned_df=churned_df[['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE']]
                fig4 = go.Figure(data=[go.Table(
                columnwidth=[2.5, 1.5, 2.5, 2.5, 3.0, 2.5, 2.5],
                header=dict(
                    values=["<b>EMP_LENGTH</b>", "<b>INT_RATE</b>", "<b>LOAN_AMNT</b>", "<b>TERM</b>", "<b>HOME_OWNERSHIP</b>","<b>ANNUL_INC</b>", "<b>TITLE</b>","<b>CREDIT SCORE</b>"],
                    fill_color='#CDCDD6',
                    font_color="#4C4C54",
                    align=['center'],
                    line_color='#ffffff',
                    font_size=14,
                    height=40
                ),
                cells=dict(values=[final_churned_df.EMP_LENGTH,final_churned_df.INT_RATE,final_churned_df.LOAN_AMNT,final_churned_df.TERM,final_churned_df.HOME_OWNERSHIP,final_churned_df.ANNUAL_INC,final_churned_df.TITLE,final_churned_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                # Update the layout of the Plotly table
                fig4.update_layout(
                    autosize=False,
                    width=970,
                    height=600,
                    margin=dict(l=0, r=0, b=0, t=0, pad=4),
                    paper_bgcolor="#ffffff"
                )
                st.subheader("List of Both Churned and Retained Applications")
                st.plotly_chart(fig4)
        else:
            st.error("Entered Invalid data, Please check your Inputs...")
if selected_opt=='Defaulter Data':
    col1, col2= st.columns([2.8,7.2])
    with col1:
      loan_amount = st.number_input('Loan Amount:',value=10000)
      home_ownership = st.selectbox('Current Home Ownership Status:',('OWN', 'RENT', 'MORTGAGE','ANY'))
      annual_income = st.number_input('Annual income:', value=120000)
      loan_type = st.selectbox('Type of loan:',
      ('Credit card refinancing','Debt consolidation','Home improvement','Major purchase','Business','Medical expenses','Moving and relocation','Vacation','Home buying','Green loan','Car financing','Other'))
      int_rate=st.number_input('Interest rate:',value=10)
      term = st.radio("Loan Repayment Tenure:",["36 months", "60 months"],horizontal=True)
      Employee_Exp = ["< 1 year","2 years","3 years","4 years","5 years","6 years","7 years","8 years","9 years","10+ years"]
      emp_length = st.select_slider("Experience:", options=Employee_Exp)
      credit_score=st.number_input('Credit Score (Optional)',value=0)
      appln_type = st.selectbox('Choose desired data for application retrieval:',
      ('Retrieve Defaulted Applications ','Retrieve Successful Applications','Retrieve Both Applications'))
      btn1=st.button('Get Data',key='button_cntr7')
    def is_valid_data(credit_score,loan_amount,annual_income,int_rate):
        if(0<=credit_score<=900  and loan_amount>=0 and annual_income>=0 and int_rate>=0):
            return True
        return False  
    with col2:
      if not btn1:
        res=session.sql('CALL LENDINGAI_DB.BASE.SP_DEFAULTER_APPLICATIONS()').collect()
        churned_df=pd.DataFrame(res).iloc[:20]
        final_churned_df=churned_df[['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE']]
        fig44 = go.Figure(data=[go.Table(
        columnwidth=[2.5, 1.5, 2.5, 2.5, 3.0, 2.5, 2.5],
        header=dict(
                      values=["<b>EMP_LENGTH</b>", "<b>INT_RATE</b>", "<b>LOAN_AMNT</b>", "<b>TERM</b>", "<b>HOME_OWNERSHIP</b>","<b>ANNUAL_INC</b>", "<b>TITLE</b>","<b>CREDIT SCORE</b>"],
                      fill_color='#CDCDD6',
                      font_color="#4C4C54",
                      align=['center'],
                      line_color='#ffffff',
                      font_size=14,
                      height=40
                  ),
                  cells=dict(values=[final_churned_df.EMP_LENGTH,final_churned_df.INT_RATE,final_churned_df.LOAN_AMNT,final_churned_df.TERM,final_churned_df.HOME_OWNERSHIP,final_churned_df.ANNUAL_INC,final_churned_df.TITLE,final_churned_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                  # Update the layout of the Plotly table
        fig44.update_layout(autosize=False,width=970,
                      height=600,
                      margin=dict(l=0, r=0, b=0, t=0, pad=4),
                      paper_bgcolor="#ffffff"
                  )
        st.subheader("List of Applications")
        st.plotly_chart(fig44)
      if btn1:
        if is_valid_data(credit_score,loan_amount,annual_income,int_rate):
            if credit_score==0:
                risk_score=602
                if int_rate>20:
                    risk_score+=80
                elif 15<=int_rate<20:
                    risk_score+=60
                elif 10<=int_rate<15:
                    risk_score+=30
                elif 5<=int_rate<10:
                    risk_score+=10
            else:
                risk_score=credit_score
            lst=[emp_length,int_rate,float(loan_amount),term,home_ownership,float(annual_income),loan_type,risk_score]
            df=pd.DataFrame([lst],columns=['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE'])
            snow_df=session.create_dataframe(df)
            snow_df.write.mode("overwrite").saveAsTable("LENDINGAI_DB.BASE.TBL_DEFAULTER_VALIDATION_DS")
            if appln_type=='Retrieve Defaulted Applications ':
                res=session.sql('CALL LENDINGAI_DB.BASE.SP_DEFAULTER_APPLICATIONS()').collect()
                df=pd.DataFrame(res)
                churned_df=df[df['LOAN_STATUS_BIN']==1]
                final_churned_df=churned_df[['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE']]
                fig2 = go.Figure(data=[go.Table(
                columnwidth=[2.5, 1.5, 2.5, 2.5, 3.0, 2.5, 2.5],
                header=dict(
                    values=["<b>EMP_LENGTH</b>", "<b>INT_RATE</b>", "<b>LOAN_AMNT</b>", "<b>TERM</b>", "<b>HOME_OWNERSHIP</b>","<b>ANNUAL_INC</b>", "<b>TITLE</b>","<b>CREDIT SCORE</b>"],
                    fill_color='#CDCDD6',
                    font_color="#4C4C54",
                    align=['center'],
                    line_color='#ffffff',
                    font_size=14,
                    height=40
                ),
                cells=dict(values=[final_churned_df.EMP_LENGTH,final_churned_df.INT_RATE,final_churned_df.LOAN_AMNT,final_churned_df.TERM,final_churned_df.HOME_OWNERSHIP,final_churned_df.ANNUAL_INC,final_churned_df.TITLE,final_churned_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                # Update the layout of the Plotly table
                fig2.update_layout(
                    autosize=True,
                    width=970,
                    height=600,
                    margin=dict(l=0, r=0, b=0, t=0, pad=4),
                    paper_bgcolor="#ffffff"
                )
                st.subheader("List of Defaulted Applications")
                st.plotly_chart(fig2)
            elif appln_type == 'Retrieve Successful Applications':
                res=session.sql('CALL LENDINGAI_DB.BASE.SP_DEFAULTER_APPLICATIONS()').collect()
                df=pd.DataFrame(res)
                churned_df=df[df['LOAN_STATUS_BIN']==0]
                final_churned_df=churned_df[['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE']]
                fig3 = go.Figure(data=[go.Table(
                columnwidth=[2.5, 1.5, 2.5, 2.5, 3.0, 2.5, 2.5],
                header=dict(
                    values=["<b>EMP_LENGTH</b>", "<b>INT_RATE</b>", "<b>LOAN_AMNT</b>", "<b>TERM</b>", "<b>HOME_OWNERSHIP</b>","<b>ANNUAL_INC</b>", "<b>TITLE</b>","<b>CREDIT SCORE</b>"],
                    fill_color='#CDCDD6',
                    font_color="#4C4C54",
                    align=['center'],
                    line_color='#ffffff',
                    font_size=14,
                    height=40
                ),
                cells=dict(values=[final_churned_df.EMP_LENGTH,final_churned_df.INT_RATE,final_churned_df.LOAN_AMNT,final_churned_df.TERM,final_churned_df.HOME_OWNERSHIP,final_churned_df.ANNUAL_INC,final_churned_df.TITLE,final_churned_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                # Update the layout of the Plotly table
                fig3.update_layout(
                    autosize=False,
                    width=970,
                    height=600,
                    margin=dict(l=0, r=0, b=0, t=0, pad=4),
                    paper_bgcolor="#ffffff"
                )
                st.subheader("List of Successful Applications")
                st.plotly_chart(fig3)
            elif appln_type == 'Retrieve Both Applications':
                res=session.sql('CALL LENDINGAI_DB.BASE.SP_DEFAULTER_APPLICATIONS()').collect()
                churned_df=pd.DataFrame(res)
                final_churned_df=churned_df[['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE']]
                fig4 = go.Figure(data=[go.Table(
                columnwidth=[2.5, 1.5, 2.5, 2.5, 3.0, 2.5, 2.5],
                header=dict(
                    values=["<b>EMP_LENGTH</b>", "<b>INT_RATE</b>", "<b>LOAN_AMNT</b>", "<b>TERM</b>", "<b>HOME_OWNERSHIP</b>","<b>ANNUL_INC</b>", "<b>TITLE</b>","<b>CREDIT SCORE</b>"],
                    fill_color='#CDCDD6',
                    font_color="#4C4C54",
                    align=['center'],
                    line_color='#ffffff',
                    font_size=14,
                    height=40
                ),
                cells=dict(values=[final_churned_df.EMP_LENGTH,final_churned_df.INT_RATE,final_churned_df.LOAN_AMNT,final_churned_df.TERM,final_churned_df.HOME_OWNERSHIP,final_churned_df.ANNUAL_INC,final_churned_df.TITLE,final_churned_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                # Update the layout of the Plotly table
                fig4.update_layout(
                    autosize=False,
                    width=970,
                    height=600,
                    margin=dict(l=0, r=0, b=0, t=0, pad=4),
                    paper_bgcolor="#ffffff"
                )
                st.subheader("List of Both Defaulted and Successful Applications")
                st.plotly_chart(fig4)
        else:
          st.error("Invalid Data")
  
