# GenAI Training - Day 3: LLM Wrapper Application (Prompt Playground)

# Objective

Build a Python-based LLM Wrapper Application that acts as a Prompt Playground for interacting with Large Language Models (LLMs). The application performs Summarization, Information Extraction, and Text Classification using reusable prompt templates, sample inputs, and the OpenRouter API.

---

# Technologies Used

- Python 3.11
- OpenRouter API
- OpenAI Python SDK
- Python Dotenv
- Markdown
- Git - Version Control

---

# Tasks Completed

## 1. Prompt Templates

Created reusable prompt templates in Markdown for:

- Summarization
- Information Extraction
- Text Classification

---

## 2. Sample Inputs

Created sample input files for testing different scenarios.

Examples include:

- Normal
- Long
- Ambiguous
- Incomplete

---

## 3. LLM Integration

- Connected the application to the OpenRouter API.
- Loaded the API key and model from the `.env` file.
- Sent prompts to the configured LLM.
- Received the generated response from the model.

---

## 4. LLM Wrapper Application

Implemented an LLM Wrapper Application that:

- Accepts the task from the user.
- Accepts the sample type from the user.
- Loads the corresponding prompt template.
- Loads the corresponding sample text.
- Builds the final prompt.
- Sends the prompt to the configured LLM.
- Receives the generated response.
- Displays the response in the terminal.
- Saves the response to the `outputs` folder.

---

## 5. Modular Project Structure

Separated the application into independent modules.

### `playground.py`

Responsible for:

- User interaction
- Loading prompt templates
- Loading sample text
- Building the final prompt
- Calling the LLM wrapper
- Displaying the response
- Saving the output

### `model_client.py`

Responsible for:

- Loading environment variables
- Creating the OpenRouter client
- Communicating with the LLM
- Sending prompts
- Returning the generated response

---

## 6. Environment Configuration

- Stored sensitive configuration values in the `.env` file.
- Added a `.env.example` file for project setup.
- Excluded sensitive files using `.gitignore`.

---

## 7. Project Documentation

- Added `requirements.txt` for dependency management.
- Created `README.md`.
- Documented the project structure and setup process.

---

# Project Structure


GenAI_Prompt_Playground/
│
├── prompts_templates/
│   ├── summarization_prompt.md
│   ├── extraction_prompt.md
│   └── classification_prompt.md
│
├── sample_texts/
│   ├── summarization/
│   ├── extraction/
│   └── classification/
│
├── outputs/
│
├── model_client.py
├── playground.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md


---

# Environment Variables

Create a `.env` file in the project root.


OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-oss-20b:free


---

# Requirements

Install the required dependencies:

- pip install -r requirements.txt


---

# Running the Project

Run the application using:

- python playground.py


The application will:

1. Select an NLP task.
2. Select a sample input.
3. Load the corresponding prompt template.
4. Build the final prompt.
5. Send the prompt to the configured LLM.
6. Display the generated response.
7. Save the response in the `outputs` folder.

---

# Current Status

- LLM Wrapper Application completed.
- Prompt templates implemented using Markdown.
- Sample input datasets created.
- OpenRouter API integrated.
- Modular project structure implemented.
- Environment variables configured.
- Output generation completed.
- Requirements file updated.
- Project documentation completed.
