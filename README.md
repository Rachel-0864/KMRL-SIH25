# KMRL-SIH25

##  Project Overview

The **KMRL Document Intelligence Hub** is an AI-powered document management system designed to help Kochi Metro Rail Limited (KMRL) efficiently manage, process, and retrieve large volumes of unstructured and multi-format documents. The system automates document extraction, classification, summarization, and semantic search, enabling faster decision-making and improved organizational efficiency.

---

##  Problem Statement

KMRL manages a vast number of documents across departments in formats such as PDFs, Word files, images, and emails. Manual handling of these documents leads to delays, information silos, compliance risks, redundant efforts, and loss of institutional knowledge. There is a need for a centralized, intelligent system to automate document understanding and retrieval.

---

##  Proposed Solution

The proposed system uses **OCR and AI-based NLP techniques** to extract text, classify documents, generate summaries, and enable semantic search. A centralized database stores all processed documents, while notifications ensure timely access to important updates.

---

##  System Architecture

The system follows a **client–server architecture**:

* **Frontend:** React.js-based user interface for document upload, search, and notifications.
* **Backend:** Flask/FastAPI server handling authentication, OCR, NLP processing, and APIs.
* **Database:** PostgreSQL with pgVector for semantic embeddings and efficient retrieval.
* **AI Layer:** OCR, classification, summarization, and semantic search pipelines.

---

##  Workflow

1. User authentication using OTP-based login
2. Document upload or email-based document ingestion
3. OCR-based text extraction from scanned or image documents
4. NLP-based classification and summarization
5. Storage of documents, metadata, and embeddings in database
6. Notification generation for relevant users
7. Semantic search and document retrieval

---

## Key Features

* Automated OCR for scanned and image documents
* AI-based document classification and summarization
* Semantic search using vector embeddings
* Secure authentication and role-based access
* Centralized document repository
* Multilingual document support

---

##  Tech Stack

* **Frontend:** React.js, HTML, CSS
* **Backend:** Python, Flask / FastAPI
* **Database:** PostgreSQL, pgVector
* **AI & NLP:** Transformers, Sentence-BERT, Torch
* **OCR:** Tesseract, PyMuPDF, pdf2image

---

##  Python Dependencies

```
Flask
flask-cors
psycopg2-binary
requests
bcrypt
sentence-transformers
torch
transformers
pdf2image
pytesseract
python-docx
PyMuPDF
python-dotenv
Pillow
pgvector
numpy
scikit-learn
scipy
```

---

##  Installation & Setup

1. Clone the repository
2. Create a virtual environment and activate it
3. Install dependencies using `pip install -r requirements.txt`
4. Configure environment variables in `.env` file
5. Run the backend server
6. Start the frontend application

---

##  Outcome

The system significantly reduces manual document review time, improves accessibility to critical information, minimizes compliance risks, and enhances inter-departmental coordination within KMRL.




Just tell me 👍
