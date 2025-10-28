# 🏛️ MIA – Municipal Intelligence Agent

<p align="center">
  <img width="460" height="450" src="https://github.com/SilvanaJ90/MIA-govtech-agent/blob/main/frontend/assets/img/mia.png">
</p>

---

### 📑 Table of Contents
1. [Version History](#version-history)  
2. [Project Information](#project-information)  
3. [Business Context](#business-context)  
4. [Project Planning](#project-planning)  
5. [Project Development](#project-development)  
6. [How to Start It](#how-to-start-it)  
7. [Video Mia](#video-mia)  
8. [Demo](#demo)  
9. [Languages and Tools](#languages-and-tools)  
10. [Authors](#authors)  

---

## 🕑 Version History
| Date       | Version | Team | Organization | Description |
|------------|---------|------|--------------|-------------|
| 29/11/2025 | 0.1     | MIA  | NoCountry    | MVP release |

---

## 📌 Project Information
| Item                | Description |
|---------------------|-------------|
| **Team**            | Mia |
| **Project**         | AI Agent for Citizen Services |
| **Start Date**      | 29/10/2025 |
| **End Date**        | 29/11/2025 |
| **Client**          | NoCountry |
| **Project Leader**  | --- |
| **Project Manager** | --- |

---

## 📊 Business Context

**Vertical:** AI Agents  
**Sector:** GovTech  

### Problem
Municipal and provincial governments receive thousands of citizen requests daily.  
Queues, phone calls, and emails overload public services, causing delays and dissatisfaction.  
An **AI-driven solution** is needed to automate repetitive queries and provide citizens with 24/7 support.  

---

## 📋 Project Planning

### Project Description
MIA AI Agent is an intelligent conversational assistant designed to **optimize citizen services in the GovTech sector** by automating responses, managing service queues, and escalating complex cases to human officials when needed.  

### General Objective
Build an **AI conversational agent** that ensures transparent, fast, and accessible citizen attention 24/7.  

### Specific Objectives
- Respond to frequently asked questions.  
- Manage appointments and citizen service requests.  
- Escalate complex queries to the appropriate government department.  
- Provide accessibility and transparency to all users.  
- Generate and export metrics to improve decision-making.  

### Project Requirements
- **Python Version**: 3.x  
- **Dependencies**: Listed in `requirements.txt`  
- **Streamlit**: Required to run the web interface  
- **Data Files**: Official documents (PDFs, regulations, FAQs)  

---

## ⚙️ Project Development
### 🛠️ Development Phases

| Phase | Description |
|-------|-------------|
| **1. Data Collection & ETL** | Extract data from FAQs, regulations, and official documents. |
| **2. Knowledge Base Creation** | Build embeddings and store them in a vector database. |
| **3. Conversational Flows** | Implement LLM + RAG for contextual responses. |
| **4. Frontend** | Deploy chatbot using Streamlit. |
| **5. Backend & APIs** | Integrate with municipal/government systems. |
| **6. Testing & Validation** | Ensure usability, accessibility, and compliance. |

---



## 🚀 How to Start It
| Step                         | Command | Description |
|------------------------------|---------|-------------|
| Clone the project            | `git clone https://github.com/SilvanaJ90/MIA-govtech-agent.git` | Clone repository |
| Create virtual environment   | `python -m venv .venv` | Create isolated Python environment |
| Activate on Windows          | `.venv\Scripts\activate` | Activate virtual environment (Windows) |
| Activate on macOS/Linux      | `source .venv/bin/activate` | Activate virtual environment (macOS/Linux) |
| Install dependencies         | `pip install -r requirements.txt` | Install all required libraries |
| **Create `.env` file** | `nano .env` | Create environment file with your API keys |
| **Add your API keys** |  | <pre>GOOGLE_API_KEY=tu_api_key_google<br>HUGGING_FACE=tu_api_key_huggingface</pre> |
| **Export environment variables (Linux/macOS)** | `export $(cat .env | xargs)` | Load API keys into environment |
| Run AI Agent                 | `streamlit run frontend/app.py` | Start the chatbot with Streamlit |
| Chat with your bot           | Open browser → `http://localhost:8501` | Interact with the AI Agent |


---

## 🎥 Video Mia
[![Video Mia]]()

---

## 💻 Demo
You can try the live demo here:  
👉 [View Demo](https://mia-govtech-agent-zcdmlh4jregg4f2djfvxsp.streamlit.app/)  

---

## 🛠️ Languages and Tools

### Backend
<p align="left">
  <a href="https://www.python.org" target="_blank">
    <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue"/>
  </a>
</p>

### ML/AI:
 <p align="left"><a href="https://www.langchain.com/" target="_blank" rel="noreferrer"> <img src="https://img.shields.io/badge/langchain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white"/> </a>
  <a href="https://gemini.google.com" target="_blank" rel="noreferrer"> <img src="https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white"/> </a>
 <a href="https://huggingface.co/" target="_blank" rel="noreferrer"> <img src="https://img.shields.io/badge/-HuggingFace-FDEE21?style=for-the-badge&logo=HuggingFace&logoColor=black"/> </a>
 </p>

### Frontend
<p align="left">
  <a href="https://streamlit.io/" target="_blank">
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white"/>
  </a>
</p>

---

## 👩‍💻 Authors
[![Mia contributors](https://contrib.rocks/image?repo=SilvanaJ90/MIA-govtech-agent)](https://github.com/SilvanaJ90/MIA-govtech-agent/graphs/contributors)  

