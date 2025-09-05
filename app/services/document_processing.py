from langchain_community.document_loaders import PyPDFLoader
from app.config import aws_settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.utils.s3 import s3_client

import tempfile
import logging
import io
import contextlib

# error-only logs
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("unstructured").setLevel(logging.ERROR)
logging.getLogger("pypdf").setLevel(logging.ERROR)


#used one existing organisation id for now.
organisation_id = "760c33f0-8d9c-4a62-b2d3-fcdd09912eb2_"  # test purpose existing organisation id (later will be from api enpoint depends logged in user organisation if exists.)

docs = []


paginator = s3_client.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket=aws_settings.AWS_S3_BUCKET, Prefix=organisation_id):
    for obj in page.get("Contents", []) or []:
        key = obj["Key"]
        if not key.lower().endswith(".pdf"):
            continue
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            s3_client.download_fileobj(aws_settings.AWS_S3_BUCKET, key, tmp)
            tmp.flush() #makes sure everything is written to disk before we open it
            pdf_loader = PyPDFLoader(tmp.name)

            # noisy stdout/stderr from PDF parser
            f_stdout = io.StringIO()
            f_stderr = io.StringIO()
            with contextlib.redirect_stdout(f_stdout), contextlib.redirect_stderr(f_stderr):
                page_docs = pdf_loader.load()  # typically returns one Document per page

            # attach S3 metadata and page number
            for i, d in enumerate(page_docs, start=1):
                d.metadata.setdefault("source", key)
                d.metadata["s3_key"] = key
                d.metadata["page"] = i
            docs.extend(page_docs)


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