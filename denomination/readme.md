# Business Name Checker - Tunisia RNE

🏢 **Intelligent Business Name Validation for Tunisia RNE (Registre National des Entreprises)**

An AI-powered Streamlit application that helps entrepreneurs validate business names for registration in Tunisia. The system checks for name availability, inappropriate content, and compliance with Tunisia's business naming regulations.

## 🎯 Features

- **Name Availability Check**: Validates against existing RNE database
- **Special Character Validation**: Ensures compliance with Tunisia naming rules
- **Inappropriate Content Detection**: Filters out hate speech and inappropriate terms
- **Multi-language Support**: Supports Arabic, French, and English
- **Alternative Name Suggestions**: Provides smart alternatives when names are unavailable
- **Interactive Chat Interface**: Natural language conversation with AI assistant
- **Real-time Analysis**: Instant feedback and recommendations

## 📁 Repository Structure

```
tunisia-business-name-checker/
├── app.py                 # Main Streamlit application
├── business_validator.py  # Business name validation logic
├── utils.py              # Utility functions for LangChain and vector stores
├── requirements.txt      # Python dependencies
├── .streamlit/           # Streamlit configuration
│   └── secrets.toml      # API keys and secrets (not in repo)
├── chroma_db/           # Vector database storage (auto-created)
│   ├── companies/       # Company names database
│   └── hate_words/      # Inappropriate content database
└── README.md            # Project documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API Key
- LangSmith API Key (optional, for monitoring)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/tunisia-business-name-checker.git
   cd tunisia-business-name-checker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create `.streamlit/secrets.toml`:
   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   LANGSMITH_API_KEY = "your-langsmith-api-key"  # Optional
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📋 Requirements.txt

```txt
streamlit>=1.28.0
langchain>=0.1.0
langchain-groq>=0.0.1
langchain-chroma>=0.1.0
langchain-core>=0.1.0
langsmith>=0.0.70
streamlit-feedback>=0.1.3
chromadb>=0.4.0
pandas>=2.0.0
numpy>=1.24.0
```

## 🔧 Configuration

### API Keys Setup

1. **Groq API Key**: Used for fast LLM inference
   - Get from: https://console.groq.com/keys
   
2. **LangSmith API Key**: Optional, for monitoring and debugging
   - Get from: https://smith.langchain.com/

### Vector Database

The application uses ChromaDB to store:
- **Company Names**: Existing business names from Tunisia RNE
- **Hate Words**: Inappropriate content database

Databases are automatically created in the `chroma_db/` directory.

## 🎨 Usage

### Basic Name Checking

```
User: "Is TechSolutions available?"
AI: [Performs comprehensive analysis and shows results]
```

### Special Characters Validation

```
User: "Check Tech@Solutions#2024"
AI: [Detects special characters and suggests clean alternatives]
```

### Business Consultation

```
User: "What makes a good business name?"
AI: [Provides expert guidance on business naming]
```

## 🏗️ Application Architecture

### 1. `app.py` - Main Application
- Streamlit UI and chat interface
- Component initialization
- Session management
- Feedback system integration

### 2. `business_validator.py` - Validation Engine
- Special character checking
- Hate word detection
- Business name similarity analysis
- Alternative name generation
- Results display formatting

### 3. `utils.py` - Utility Functions
- Vector store initialization
- LangChain chain creation
- Environment validation
- Sample data loading

## 🔍 Validation Rules

### ✅ Allowed Characters
- Letters: A-Z, a-z, Arabic letters (أ-ي)
- Numbers: 0-9
- Spaces
- Basic punctuation: `. - ' &`

### ❌ Prohibited
- Special characters: `@ # $ % ^ * ( ) + = [ ] { } | \ : ; " < > ? / ~`
- Inappropriate content
- Exact duplicates of existing names

## 📊 Status Levels

- **AVAILABLE**: ✅ Safe to register
- **NOT AVAILABLE**: ❌ Exact match found
- **HIGH RISK**: ⚠️ Very similar names exist
- **MEDIUM RISK**: ⚠️ Potential conflicts
- **BLOCKED**: 🚫 Contains prohibited content/characters

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Production Deployment

**Streamlit Cloud:**
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in dashboard
4. Deploy

**Docker:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🛠️ Customization

### Adding New Company Names
```python
# In utils.py
def add_company_to_database(companies_store, company_data):
    companies_store.add_texts(
        texts=[company_data],
        metadatas=[{"type": "company", "source": "rne"}]
    )
```

### Modifying Validation Rules
```python
# In business_validator.py
def check_special_characters(name: str) -> tuple:
    # Customize allowed characters here
    allowed_chars = set('your_custom_chars')
    # ... rest of the function
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit: `git commit -m 'Add feature'`
6. Push: `git push origin feature-name`
7. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Email**: support@yourcompany.com

## 🔄 Version History

- **v1.0.0**: Initial release with core validation features
- **v1.1.0**: Added Arabic language support
- **v1.2.0**: Enhanced alternative name suggestions
- **v1.3.0**: Improved UI and feedback system

---

**Made with ❤️ for Tunisia's entrepreneurial community**
