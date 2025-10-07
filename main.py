import os
import streamlit as st
import tempfile
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)
from langchain_core.messages import HumanMessage

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


st.set_page_config(page_title="Multi AI Chatbot", layout="centered")


if "page" not in st.session_state:
    st.session_state.page = "home"

# Navigation Buttons
def home():
    st.title(" Welcome to My AI Multi-Tool Chatbot App")
    st.write("Choose a feature:")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Chatbot"):
            st.session_state.page = "youtube"

    with col2:
        if st.button("You Tube Chat"):
            st.session_state.page = "chatbot"

    with col3:
        if st.button(" PDF Chat"):
            st.session_state.page = "pdf"

       

# YouTube Page
def youtube_page():
    st.header("📺 YouTube Video Q&A Bot")

    youtube_url = st.text_input(" Enter full YouTube link:")
    question = st.text_input(" Your Question about the video:")

    def extract_video_id(url):
        try:
            parsed_url = urlparse(url)
            if parsed_url.hostname == "youtu.be":
                return parsed_url.path[1:]
            query = parse_qs(parsed_url.query)
            return query["v"][0]
        except:
            return None

    if youtube_url and question:
        video_id = extract_video_id(youtube_url)

        if video_id:
            try:
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["hi"])
                except:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                text = " ".join([t["text"] for t in transcript])
                chunks = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200).create_documents([text])
                embed = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
                db = Chroma.from_documents(chunks, embed, persist_directory=f"./chroma_db/{video_id}")
                db.persist()
                retriever = db.as_retriever()
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
                qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
                with st.spinner("Thinking..."):
                    result = qa.invoke({"query": question})
                    st.success("Answer:")
                    st.write(result["result"])
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Invalid YouTube link")

# Gemini Chatbot Page
def chatbot_page():
    st.header("Gemini API Chatbot")
    prompt = st.text_input(" Ask anything:")

    if st.button("Get Answer"):
        if prompt:
            try:
                llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
                response = llm.invoke([HumanMessage(content=prompt)])
                st.success("Answer:")
                st.write(response.content)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a prompt")

# PDF Chat Page
def pdf_page():
    st.header(" Chat with your PDF")
    pdf_file = st.file_uploader("📎 Upload PDF", type="pdf")

    if pdf_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.read())
            pdf_path = tmp.name

        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        chunks = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)

        embed = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
        vectordb = Chroma.from_documents(chunks, embed)
        retriever = vectordb.as_retriever()
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        user_q = st.text_input("Ask a question about the PDF:")
        if user_q:
            with st.spinner("Thinking..."):
                response = qa.invoke({"query": user_q})
                st.success(" Answer:")
                st.write(response["result"])



                  

# Route pages
if st.session_state.page == "home":
    home()
elif st.session_state.page == "chatbot":
    youtube_page()
    if st.button(" Back to Home"):
        st.session_state.page = "home"
elif st.session_state.page == "youtube":
    chatbot_page()
    if st.button(" Back to Home"):
        st.session_state.page = "home"
elif st.session_state.page == "pdf":
    pdf_page()
    if st.button("Back to Home"):
        st.session_state.page = "home"

     
