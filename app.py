import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import TensorflowHubEmbeddings
from langchain.vectorstores import FAISS

def get_text(documents):
    text=""
    for document in documents:
        reader = PdfReader(document)
        for page in reader.pages:
            text += page.extract_text()
    return text

def get_chunks(text):
    splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len
    )
    return splitter.split_text(text)

def create_database(chunks):
    embeddings = TensorflowHubEmbeddings()
    database = FAISS.from_texts(texts=chunks, embedding=embeddings)
    return database

def main():
    load_dotenv()

    st.set_page_config(
        page_title="Chat with your documents", 
        page_icon=":books:"
    )
    st.header("Chat with your documents :books:")
    st.text_input("Ask a question about your documents: ")

    with st.sidebar:
        st.subheader("Your documents")
        documents = st.file_uploader(
            "Upload your PDFs and click on Process", accept_multiple_files=True
        )
        if st.button("Process"):
            with st.spinner("Processing"):
                raw_text = get_text(documents)
                text_chunks = get_chunks(raw_text)
                vector_database = create_database(text_chunks)


if __name__ == "__main__":
    main()
