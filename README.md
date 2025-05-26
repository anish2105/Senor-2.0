# 🧑‍⚖️ Senor 2.0

**Senor 2.0** is an LLM-powered chatbot designed to help Indian citizens understand and navigate legal procedures. It ingests legal documents from various sources, semantically processes them, and responds with context-rich, updated legal guidance.

---

## 🚀 Overview

* Reads legal data from SQL databases, JSON files, and PDFs.
* Uses **LangChain** for semantic chunking of documents.
* Generates vector embeddings using **Gemini's `embedding-001`** model.
* Stores and retrieves relevant document chunks from **Pinecone**.
* Re-ranks retrieved chunks using **Pinecone's `bge-reranker-v2-m3`**.
* Runs LLM calls using **Gemini-2.0-flash** for answering user queries.
* Integrates an AI agent via **Agno** to fetch up-to-date responses using DuckDuckGo.
* Evaluates and monitors chatbot performance using **Opik**.
* Provides RESTful API access using **FastAPI**.

---

## 🧱 Core Infrastructure

### 🔁 RAG Pipeline

* Ingests legal documents from SQL, JSON, and PDF sources.
* Modular pipeline for easy integration of new data sources.
* Semantic chunking for improved context and recall.

### 📦 Pinecone Vector DB

* Stores document embeddings for retrieval.
* Uses `bge-reranker-v2-m3` to enhance relevance of search results.

### ⚡ FastAPI

* Exposes endpoints for query processing, data fetching, and user interactions.

### 🤖 Agno AI Agent

* Adds real-time search capability using DuckDuckGo.
* Option to refine or replace RAG answers with updated information.

### 📊 Opik

* Enables LLM response evaluation and monitoring.
* Tracks performance metrics and answer quality.

---

## 🛠 Tech Stack

* **Python**
* **LangChain**
* **FastAPI**
* **Docker**
* **Pinecone**
* **Gemini**
* **Opik**
* **Agno**

---

## ⚙️ Prerequisites

Before you begin, ensure you have the following:

* Docker
* Python 3.10+
* Pinecone API Key
* Gemini API Key
* Opik API Key

---