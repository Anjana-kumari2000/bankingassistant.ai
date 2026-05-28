# Banking Assistant AI

An AI-powered Banking Assistant chatbot built using Python, Rasa, HTML, CSS, JavaScript, and SQLite/MySQL.
The chatbot helps users perform banking-related tasks such as checking balances, loan inquiries, account information, EMI details, transaction support, 
and customer assistance through natural language conversations.

# Objective of Banking Assistant AI Project

-The main objective of the Banking Assistant AI project is to develop an 
intelligent AI-powered banking chatbot that can automate customer support services using Natural Language Processing (NLP)
and Machine Learning.

-The project is designed to help users interact with banking services through 
conversational messages instead of traditional manual support systems.

# Main Objectives
-Automate banking customer support
-Provide instant responses to customer queries
-Reduce manual workload of bank employees
-Improve customer experience using AI chatbot technology
-Understand user messages using NLP
-Handle banking-related conversations intelligently
-Provide loan and EMI information
-Support account-related assistance
-Create a real-time chatbot using Rasa
-Integrate frontend, backend, and database systems
-Learn chatbot development using Python and AI technologies

# Recommended Versions for Banking Assistant AI
-Software	Version
-Python	3.10.11 or 3.13.3
-Rasa	3.6.20

# Software Requirements for Banking Assistant AI
| Software           | Purpose             |
| ------------------ | ------------------- |
| Python             | Backend development |
| Rasa               | Chatbot and NLP     |
| Visual Studio Code | Code editor         |
| Git                | Version control     |
| GitHub             | Project hosting     |
| SQLite             | Database storage    |
| MySQL              | Banking database    |
| Postman            | API testing         |
| Google Chrome      | Running chatbot UI  |
| Command Prompt     | Running commands    |
| PowerShell         | Terminal commands   |

#🚀 How To Run Project
-git clone https://github.com/Anjana-kumari2000/bankingassistant.ai.git

-cd bankingassistant.ai

-python -m venv .venv

-.venv\Scripts\activate

-pip install -r requirements.txt

-pip install rasa==3.6.20

-rasa train

-rasa run --enable-api --cors "*"

-rasa run actions

-python app.py
