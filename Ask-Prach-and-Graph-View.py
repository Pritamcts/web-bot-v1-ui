# Import necessary libraries
import streamlit as st
import logging
import requests



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the API endpoint
API_ENDPOINT = "http://3.91.69.147:5001"  # Adjust this to your actual API endpoint

def upload_pdf(file):
    files = {'file': file}
    response = requests.post(f"{API_ENDPOINT}/process_pdf", files=files)
    return response.json()

def get_answer(question):
    payload = {"question": question}
    response = requests.post(f"{API_ENDPOINT}/api/get-answer", json=payload)
    return response.json()

def format_citations_for_table(citations):
    table_data = []
    for citation in citations:
        source = citation['source']
        pages = citation['pages']
        chunks = citation['chunks']
        chunks_text = ', '.join([f"chunk{i+1}: {chunk}" for i, chunk in enumerate(chunks[:3])])
        if len(chunks) > 3:
            chunks_text += '...'
        table_data.append({"Source": source, "Pages": pages, "Content": chunks_text})
    return table_data

def main():
    st.set_page_config(page_title="Prach Mortgage Assistant", layout="wide", page_icon="prach-logo.svg")

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .big-font {
            font-size:30px !important;
            font-weight: bold;
            color: #1E90FF;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white !important;
            padding: 10px 24px;
            border-radius: 8px;
            border: none;
        }
        .stButton>button:active {
            background-color: #4CAF50;
            color: white !important;
        }
        .stButton>button:focus {
            background-color: #4CAF50;
            color: white !important;
        }
        .stButton>button:hover {
            background-color: #29772E;
            color: white !important;
        }
        .stTextInput>div>div>input {
            background-color: #F0F8FF;
        }
        .answer-text {
            font-size:15px !important;
            font-weight: bold;
        }
        .citation-table th {
            background-color: #4CAF50;
            color: white;
        }
        .citation-table td {
            padding: 10px;
            text-align: left;
        }
        .sidebar .sidebar-content {
            padding: 20px;
        }
        .sidebar .sidebar-content hr {
            border: 1px solid #ddd;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## Upload your PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            with st.spinner(f"🔄 Processing {uploaded_file.name}..."):
                response = upload_pdf(uploaded_file)
                st.success("PDF processed and stored in knowledge graph")
        st.markdown("---")
        st.sidebar.markdown("## Enter Website URL")
        website_url = st.sidebar.text_input("Website URL", key="website_url_input")
        if st.sidebar.button("Process Website"):
            if website_url:
                with st.spinner(f"🔄 Processing {website_url}..."):
                    try:
                        response = requests.post(f"{API_ENDPOINT}/process-url", json={"url": website_url})
                        print(website_url)
                        print(response)
                        if response.status_code == 200:
                            st.sidebar.success("Website processed and stored in knowledge graph")
                        else:
                            # Try to get JSON error message, fall back to status code if not possible
                            try:
                                error_message = response.json().get('error', f"Error: HTTP {response.status_code}")
                            except requests.exceptions.JSONDecodeError:
                                error_message = f"Error: HTTP {response.status_code}. The server did not return a valid JSON response."
                            st.sidebar.error(error_message)
                    except requests.exceptions.RequestException as e:
                        st.sidebar.error(f"Error connecting to the server: {str(e)}")
            else:
                st.sidebar.warning("Please enter a website URL")
        st.markdown("---")
        st.markdown("## Mortgage Assistant Bot Description")
        st.markdown("""
        I'm an AI assistant specialized in mortgage lending. I can help you understand complex mortgage topics, from PMI to loan types, using my knowledge of underwriting guidelines and official documents. Whether you're buying your first home or refinancing, I'm here to provide accurate information and guide you through the process. For specific rate or cost inquiries, please consult your loan officer.
        """)

    # Main content
    col1, col2, col3 = st.columns([1,4,1])
    with col1:
        st.image("prach-logo.svg", width=80)
    st.markdown('<p class="big-font">Prach Mortgage Assistant using Knowledge Graph</p>', unsafe_allow_html=True)

    st.markdown("## Ask a question :")
    question = st.text_input("Your question:", key="question_input")

    if st.button("Get Answer"):
        if question:
            with st.spinner("Thinking..."):
                result = get_answer(question)
                answer = result.get("answer", "Sorry, I couldn't generate an answer.")
                citations = result.get("citation", [])
                table_data = format_citations_for_table(citations)

            st.markdown("### Answer:")
            st.write(answer)

            if table_data:
                st.markdown("### Citations:")
                st.markdown(
                    '<table class="citation-table">'
                    '<thead><tr><th>Source</th><th>Pages</th><th>Content</th></tr></thead>'
                    '<tbody>'
                    + ''.join(f'<tr><td>{row["Source"]}</td><td>{row["Pages"]}</td><td>{row["Content"]}</td></tr>' for row in table_data)
                    + '</tbody></table>',
                    unsafe_allow_html=True
                )
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()

# Clear cache when the app is done
st.cache_resource.clear()
st.cache_data.clear()
