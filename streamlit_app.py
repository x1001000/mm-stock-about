import streamlit as st
import pandas as pd
import openai

from pydantic import BaseModel
class BilingualEditions(BaseModel):
    en_US: str
    zh_TW: str

from opencc import OpenCC
cc = OpenCC('s2twp')

def process_batch_openai(df, system_prompt):
    """
    Process a DataFrame batch using OpenAI's API
    
    Args:
        df (pd.DataFrame): DataFrame with 'Source' column
        system_prompt (str): System prompt to guide the AI's responses
    
    Returns:
        pd.DataFrame: DataFrame with added 'Output' column
    """
    # Ensure the OpenAI API key is set
    if 'OPENAI_API_KEY' not in st.secrets:
        st.error("OpenAI API key not found. Please set it in Streamlit secrets.")
        return df
    
    # Set up OpenAI client
    client = openai.OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
    
    # Create a progress bar
    progress_bar = st.progress(0)
    
    # Process each row
    en_US, zh_TW = [], []
    for index, row in df.iterrows():
        try:
            # Make API call
            response = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": str(row['Source'])}
                ],
                response_format=BilingualEditions,
            )
            
            # Extract the response text
            en_US.append(response.choices[0].message.parsed.en_US)
            zh_TW.append(cc.convert(response.choices[0].message.parsed.zh_TW))
        
        except Exception as e:
            st.write(f"Error: {str(e)}")
            raise
        
        # Update progress bar
        progress_bar.progress((index + 1) / len(df))
    
    # Add outputs to the DataFrame
    df['en_US'] = en_US
    df['zh_TW'] = zh_TW
    
    return df

def main():
    st.title("文字生成批次處理工具")
    
    # Sidebar for system prompt
    st.sidebar.header("請先小量測試，找出效果最佳的系統提示詞")
    system_prompt = st.sidebar.text_area(
        "這裡寫的是 system/developer prompt，上傳的檔案的每一列是 user prompt，兩個 prompt 同時送入 GPT-4o 做一次文字生成（inference），以迴圈的方式處理每一列", 
        "我們要開發一個財報專區，需要請你重新整理使用者輸入的內容，產出適合大眾閱讀的公司介紹。若使用者輸入的內容有公司創立時間、總部地點，則放在最前面，若內容很簡短，就維持其內容即可無需增加內容，若內容較長，要適時分段提升可讀性。\n\n撰寫英文及台灣繁體中文兩個版本，台灣繁體中文使用台灣用語，不要使用中國大陸用語，不要使用 Markdown 語法，不要有超連結。",
        height=500
    )
    
    # File uploader
    uploaded_file = st.file_uploader(
        "上傳 Excel 或 CSV 檔，要有一欄的標題命名為 Source", 
        type=['csv', 'xlsx']
    )
    
    if uploaded_file:
        # Read the file
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Display original DataFrame
            st.subheader("Original Data")
            # With magic:
            df
            
            # Check if 'Source' column exists
            if 'Source' not in df.columns:
                st.error("The uploaded file must have an 'Source' column.")
                return
            
            if 'df_processed' in st.session_state:
                st.subheader("Processed Data")
                st.session_state.df_processed
                return

            # Process button
            if st.button("按我批次處理每一列"):
                # Validate OpenAI API key
                if 'OPENAI_API_KEY' not in st.secrets:
                    st.error("Please set OpenAI API key in Streamlit secrets.")
                    return
                
                # Process the batch
                processed_df = process_batch_openai(df, system_prompt)
                
                # Display processed DataFrame
                st.subheader("Processed Data")
                # With magic:
                processed_df
                
                # Download button for Excel
                import io
                buffer = io.BytesIO()
                processed_df.to_excel(buffer, index=False, engine='openpyxl')
                st.download_button(
                    label="按我下載 processed.xlsx",
                    data=buffer.getvalue(),
                    file_name='processed.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

                st.session_state.df_processed = processed_df
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    elif 'df_processed' in st.session_state:
        del st.session_state.df_processed

if __name__ == "__main__":
    main()