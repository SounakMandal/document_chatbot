import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from html_template import css, bot_template, user_template


def get_text(documents):
    text = ""
    for document in documents:
        reader = PdfReader(document)
        for page in reader.pages:
            text += page.extract_text()
    return text


def get_chunks(text):
    splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=100, length_function=len
    )
    return splitter.split_text(text)


def create_database(chunks):
    embeddings = OpenAIEmbeddings()
    return FAISS.from_texts(texts=chunks, embedding=embeddings)


def get_conversation_chain(database):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    return ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=database.as_retriever(), memory=memory
    )


def main():
    # Load configuration variables
    load_dotenv()

    # Initialize persistent variables
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    # Set page header
    st.set_page_config(page_title="Chat with your documents", page_icon=":books:")
    st.header("Chat with your documents :books:")
    st.markdown(css, unsafe_allow_html=True)

    # Use the sidebar to get the documents
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
                st.session_state.conversation = get_conversation_chain(vector_database)

    # Display the container that stores all the conversations
    conversation_container = st.container()
    placeholder = st.empty()
    error = st.empty()

    # Display the query ans answer
    query = placeholder.text_input(
        label="Ask a question about your documents", key="input_box", value=""
    )
    if query:
        if st.session_state.conversation is None:
            error.write("No documents provided")
        else:
            error.empty()
            response = st.session_state.conversation({"question": query})
            for index, message in enumerate(response["chat_history"]):
                if index % 2 == 0:
                    conversation_container.write(
                        user_template.replace("{{MSG}}", message.content),
                        unsafe_allow_html=True,
                    )
                else:
                    conversation_container.write(
                        bot_template.replace("{{MSG}}", message.content),
                        unsafe_allow_html=True,
                    )


if __name__ == "__main__":
    main()
