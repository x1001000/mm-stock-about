import streamlit as st
import pandas as pd
import openai

def process_batch_openai(df, system_prompt):
    """
    Process a DataFrame batch using OpenAI's API
    
    Args:
        df (pd.DataFrame): DataFrame with 'Input' column
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
    outputs = []
    for index, row in df.iterrows():
        try:
            # Make API call
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": str(row['Input'])}
                ]
            )
            
            # Extract the response text
            output = response.choices[0].message.content
            outputs.append(output)
        
        except Exception as e:
            outputs.append(f"Error: {str(e)}")
        
        # Update progress bar
        progress_bar.progress((index + 1) / len(df))
    
    # Add outputs to the DataFrame
    df['Output'] = outputs
    
    return df

def main():
    st.title("GPT-4o Batch Processing App")
    
    # Sidebar for system prompt
    st.sidebar.header("System Prompt Configuration")
    system_prompt = st.sidebar.text_area(
        "Enter System Prompt", 
        "Translate the About section of a company into Traditional Chinese used in Taiwan. Start the translation with the company's founding year and headquarter location in front. Maintain a formal business tone and use industry-specific terminology. Ensure proper localization to match Taiwanese business culture and language preferences. Avoid using simplified Chinese characters or informal language.",
        height=500
    )
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Excel or CSV File. Must contain 'Input' column.", 
        type=['csv', 'xlsx']
    )
    
    if uploaded_file is not None:
        # Read the file
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Display original DataFrame
            st.subheader("Original Data")
            st.dataframe(df)
            
            # Check if 'Input' column exists
            if 'Input' not in df.columns:
                st.error("The uploaded file must have an 'Input' column.")
                return
            
            if 'df_processed' in st.session_state:
                st.subheader("Processed Data")
                st.dataframe(st.session_state.df_processed)
                return

            # Process button
            if st.button("Process with GPT-4o"):
                # Validate OpenAI API key
                if 'OPENAI_API_KEY' not in st.secrets:
                    st.error("Please set OpenAI API key in Streamlit secrets.")
                    return
                
                # Process the batch
                processed_df = process_batch_openai(df, system_prompt)
                
                # Display processed DataFrame
                st.subheader("Processed Data")
                st.dataframe(processed_df)
                
                # Download button for Excel
                import io
                buffer = io.BytesIO()
                processed_df.to_excel(buffer, index=False, engine='openpyxl')
                st.download_button(
                    label="Download Processed File",
                    data=buffer.getvalue(),
                    file_name='processed.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

                st.session_state.df_processed = processed_df
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()