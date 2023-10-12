import streamlit as st  # pip install streamlit
import pandas as pd  # pip install pandas
import plotly.express as px  # pip install plotly-express
import base64  # Standard Python Module
from io import StringIO, BytesIO  # Standard Python Module
import openai
import json



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
api_key = "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"


Lv = []
key = st.text_input('Enter API key:')
openai.api_key = key
groupby_column = st.selectbox('Choose an option?',('Enter a text of your choice','Upload an Excel(.xlsx) file'))
if key:
    if groupby_column == 'Enter a text of your choice':
        text = st.text_input('Enter your text here')
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
            if col:
                 for i in df[col]:
                    try:
                        conversation = [
                    {"role": "user", "content": "Extract 'Company Name' of the product and the domain of the product like 'toy', 'Electronic' etc. from {} in   the form of Dictionary with keys - ['Company','Product Domain']. Remember that domain is very broad categorization example:-laptoms should have a domain  Electronics".format(i)},
                               ]
    
            # Generate a response from GPT-3
                        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=conversation
                 )
    
            # Extract and return the chatbot's reply
                        chatbot_reply = response["choices"][0]["message"]["content"]
                        print(chatbot_reply)
                        ini_string = json.dumps(chatbot_reply)
                        final_dictionary = json.loads(ini_string)
                        Lv.append(final_dictionary)
                    except:
                        pass
        final = pd.DataFrame()
        final['JSONData'] = Lv
        #df = pd.concat([final.drop(['JSONData'], axis=1), pd.json_normalize(final['JSONData'].apply(json.loads))], axis=1)
        # -- DOWNLOAD SECTION
        st.subheader('Downloads:')
        generate_excel_download_link(final)
        #generate_html_download_link(fig)
