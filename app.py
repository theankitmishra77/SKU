import streamlit as st  # pip install streamlit
import pandas as pd  # pip install pandas
import plotly.express as px  # pip install plotly-express
import base64  # Standard Python Module
from io import StringIO, BytesIO  # Standard Python Module
import openai
import openpyxl
import json
import os
import ast
import time

from dotenv import load_dotenv

load_dotenv()


def generate_excel_download_link(df):
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_download.xlsx">Download Excel File</a>'
    return st.markdown(href, unsafe_allow_html=True)

def generate_html_download_link(fig):
    # Credit Plotly: https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426/2
    towrite = StringIO()
    fig.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="plot.html">Download Plot</a>'
    return st.markdown(href, unsafe_allow_html=True)


st.set_page_config(page_title='Product Analysis')
st.title('Product Analysis 📈')
st.subheader('Feed me with your Excel file or Text')
#api_key = "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"

openai.api_key = st.secrets["OPENAI_KEY"]

Lv = []
Lv2 = []
groupby_column = st.selectbox('Choose an option?',('Enter a text of your choice','Upload an Excel(.xlsx) file'))

if groupby_column == 'Enter a text of your choice':
    text = st.text_input('Enter your text here')
    submit = st.button("Submit", type="primary")
    if submit:
        conversation = [
                {"role": "user", "content": "Extract 'Company Name' of the product and the domain of the product like 'toy', 'Electronic' etc. from {} in   the form of Dictionary with keys - ['Company','Product Domain']. Remember that domain is very broad categorization example:-laptoms should have a domain  Electronics".format(text)},
                           ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
         )

   # Extract and return the chatbot's reply
        chatbot_reply = response["choices"][0]["message"]["content"]
        st.write(chatbot_reply)
else:
    uploaded_file = st.file_uploader('Choose a XLSX file', type='xlsx')
    if uploaded_file:
        st.markdown('---')
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        col = st.text_input('Enter the column name')
        submit = st.button("Submit", type="primary")
        df2 = pd.DataFrame()
        final = pd.DataFrame()
        previous = []
        if submit:
            if col:
                for i in df[col]:
                    print(i)
                    try:
                        conversation = [
                {"role": "user", "content": "Extract 'Company Name' of the product and the domain of the product like 'toy', 'Electronic' etc. from {} in   the form of Dictionary with keys - ['Company','Product Domain']. Remember that domain is very broad categorization example:-laptops should have a domain  'Electronics'".format(i)},
                           ]
                        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
             )
                        chatbot_repl = response["choices"][0]["message"]["content"]
                        print(chatbot_repl)
                        chatbot_reply = chatbot_repl.replace("'",'"')
                        #print(type(chatbot_reply))
                        ini_string = json.dumps(chatbot_reply)
                        final_dictionary = json.loads(ini_string)
                        #print(type(final_dictionary))
                        data = json.loads(final_dictionary)
                        #print('lo')
                        df2 = pd.DataFrame([data]);previous.append(i)
                        print(df2)
                        try:
                            df2 = df2.rename(columns={"Company": "Company", "Product Domain": "Product"})
                            final = pd.concat([final,df2])
                        except:
                            pass
                    except:
                        pass
            time.sleep(1)
        final['Description'] = previous
        final
        # -- DOWNLOAD SECTION
        st.subheader('Downloads:')
        generate_excel_download_link(final)
       #generate_html_download_link(fig)
