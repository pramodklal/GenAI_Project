from setuptools import find_packages, setup

setup(
    name="RAGCHATBOT",
    version="0.0.1",
    author="Pramod",
    author_email="pramodklal@gmail.com",
    packages=find_packages(),
    install_requires=['langchain','langchain_community','google-generativeai','docx2txt','faiss-cpu','PyPDF2',
                      'streamlit','langchain_google_genai','python-dotenv','python-docx','Pillow']
)