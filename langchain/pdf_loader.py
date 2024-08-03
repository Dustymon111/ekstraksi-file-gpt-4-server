from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_split_pdf(pdf_path):
    # Initialize the PDF loader
    loader = PyPDFLoader(pdf_path)
    
    text_splitter = RecursiveCharacterTextSplitter(
        separators=" ",
        chunk_size=512,
        chunk_overlap=64,
    )
    # Load and split the PDF into pages
    pages = loader.load_and_split(text_splitter= text_splitter)
    
    return pages