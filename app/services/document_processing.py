from langchain_community.document_loaders import S3DirectoryLoader
from app.config import aws_settings
from langchain_text_splitters import RecursiveCharacterTextSplitter


#used one existing organisation id for now.
organisation_id = "4b3ed60e-a617-4e09-9556-373a686b1be6_"  # All files which starts with organisation id prefix

loader = S3DirectoryLoader(
    bucket=aws_settings.AWS_S3_BUCKET,
    prefix=organisation_id,
    aws_access_key_id=aws_settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=aws_settings.AWS_SECRET_ACCESS_KEY,
)
docs = loader.load()

#split in chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, 
                                               chunk_overlap=200, 
                                               add_start_index=True)


all_splits = text_splitter.split_documents(docs)



"""
#if you get a ntlk punk error please run one time at the top of the code the code below.

import ssl
import nltk

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
"""