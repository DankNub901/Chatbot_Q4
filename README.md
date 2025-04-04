
# 📊 **CIBC Q4 Financial Report Chatbot**

A **Streamlit-based** chatbot that analyzes **CIBC's Q4 Fiscal Report** and answers questions about **financial metrics** and **performance indicators**.

---

## 🚀 **Features**

- **📄 PDF Data Extraction**: Automatically extracts financial data from CIBC's Q4 fiscal report PDF.
- **🔍 Multi-Section Analysis**: Handles both **Financial Highlights** and **Canadian Personal and Business Banking** sections.
- **💬 Interactive Chat Interface**: User-friendly chat interface for asking questions about financial metrics.
- **🤖 Smart Answer Matching**: Uses fuzzy string matching to understand and answer questions accurately.
- **📈 Data Visualization**: Displays extracted metrics and provides formatted responses.

---

## 🛠 **Installation**

1. **Clone the repository**

2. **Install the required dependencies**:
```bash
pip install -r requirements.txt
```

> **Note**: This project requires **Java** to be installed for PDF extraction (required by `tabula-py`).

---

## 🚶‍♂️ **Usage**

1. **Run the Streamlit app**:
```bash
python -m streamlit run app.py
```

2. **Upload your CIBC Q4 Fiscal Report PDF** using the file uploader in the interface.

3. **Ask questions** about the financial metrics, such as:

**📈 Financial Highlights:**
- "What was the total revenue?"
- "Tell me about the net income."
- "What was the efficiency ratio?"

**🏦 Canadian Personal and Business Banking:**
- "What was the personal banking revenue?"
- "Tell me about business banking performance."
- "What were the retail banking expenses?"

---

## 🧑‍💻 **Technical Details**

The chatbot uses several key technologies and approaches:

- **📑 PDF Processing**: Uses `tabula-py` for extracting tabular data from PDFs.
- **🧠 Natural Language Processing**: Implements fuzzy string matching for question understanding.
- **🧹 Data Cleaning**: Robust cleaning and formatting of financial values.
- **🗂 Section Awareness**: Intelligent section detection and context-based answering.
- **⚙️ Dynamic Metric Calculation**: Calculates derived metrics like **efficiency ratios**.

---

## 📂 **Project Structure**

```
cibc-q4-chatbot/
├── app.py              # Main application file
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
```

---

## 📦 **Dependencies**

- `streamlit` - For building the interactive web interface.
- `pandas` - Data manipulation and analysis.
- `tabula-py` - PDF data extraction from tables.
- `PyPDF2` - To extract text from PDF.
- `python-difflib` - Fuzzy string matching for question-answering.
- **Java Runtime Environment (JRE)** - Required for `tabula-py` to function properly.

---

## 🙌 **Contributing**

Contributions are welcome! If you'd like to contribute to the project, please feel free to submit a **Pull Request**.

---

## 🤝 **Acknowledgments**

- **CIBC** for providing the Q4 fiscal report data.
- **Streamlit** for the excellent web app framework.
- **Tabula-py** for PDF data extraction capabilities.

---

## ⚠️ **Disclaimer**

This chatbot is for **informational purposes only**. Always verify financial data with official CIBC reports and documents.
```
