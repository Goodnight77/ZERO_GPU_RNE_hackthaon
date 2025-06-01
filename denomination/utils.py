import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate

def initialize_vector_stores(openai_key):
    """Initialize vector stores for companies and hate words"""
    try:
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(
            api_key=openai_key,
            model="text-embedding-3-small"
        )
        
        # Initialize company names vector store
        companies_store = Chroma(
            collection_name="tunisia_companies",
            embedding_function=embeddings,
            persist_directory="./chroma_db/companies"
        )
        
        # Initialize hate words vector store
        hate_store = Chroma(
            collection_name="hate_words",
            embedding_function=embeddings,
            persist_directory="./chroma_db/hate_words"
        )
        
        return companies_store, hate_store
        
    except Exception as e:
        print(f"Error initializing vector stores: {str(e)}")
        return None, None

def get_business_name_chain(llm, companies_store):
    """Create a business name consultation chain"""
    
    business_consultation_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert business name consultant for Tunisia RNE (Registre National des Entreprises).

Your expertise includes:
- Tunisia business registration requirements
- RNE naming conventions and rules
- Business name best practices
- Legal compliance guidance
- Creative naming suggestions

Guidelines:
- Be helpful and professional
- Provide practical advice
- Reference Tunisia-specific requirements
- Suggest actionable next steps
- Stay focused on business naming

Special Rules for Business Names in Tunisia:
- Only letters, numbers, spaces, and basic punctuation (. - ' &) are allowed
- No special characters like @ # $ % ^ * ( ) + = [ ] {{ }} | \\ : ; " < > ? / ~
- Names must be unique in the RNE database
- Both Arabic and French names are acceptable
- Avoid inappropriate or offensive content

When users ask general questions, provide helpful guidance about business naming in Tunisia.
Keep responses concise and actionable."""),
        
        ("human", "{query}")
    ])
    
    # Create the chain
    chain = business_consultation_prompt | llm
    
    return chain

def setup_chroma_directories():
    """Setup ChromaDB directories if they don't exist"""
    directories = [
        "./chroma_db",
        "./chroma_db/companies", 
        "./chroma_db/hate_words"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

def load_sample_data(companies_store, hate_store):
    """Load sample data into vector stores (for testing/demo purposes)"""
    try:
        # Sample company names (in a real implementation, this would load from a database)
        sample_companies = [
            "ID: 001\nNOM_AR: الشركة التونسية للتكنولوجيا\nNOM_FR: Société Tunisienne de Technologie",
            "ID: 002\nNOM_AR: مؤسسة النور للخدمات\nNOM_FR: Entreprise Nour Services",
            "ID: 003\nNOM_AR: شركة المستقبل للتجارة\nNOM_FR: Société Avenir Commerce",
            "ID: 004\nNOM_AR: تكنولوجي سولوشنز\nNOM_FR: TechSolutions SARL",
            "ID: 005\nNOM_AR: الشركة الذكية للبرمجيات\nNOM_FR: Smart Software Company"
        ]
        
        # Sample hate words/inappropriate content
        sample_hate_words = [
            {"content": "badword1", "type": "inappropriate"},
            {"content": "offensive2", "type": "hate_speech"},
            {"content": "inappropriate3", "type": "vulgar"}
        ]
        
        # Add companies to vector store
        if companies_store and len(sample_companies) > 0:
            companies_store.add_texts(
                texts=sample_companies,
                metadatas=[{"type": "company", "id": i+1} for i in range(len(sample_companies))]
            )
        
        # Add hate words to vector store
        if hate_store and len(sample_hate_words) > 0:
            hate_texts = [item["content"] for item in sample_hate_words]
            hate_metadatas = [{"type": item["type"]} for item in sample_hate_words]
            hate_store.add_texts(
                texts=hate_texts,
                metadatas=hate_metadatas
            )
        
        return True
        
    except Exception as e:
        print(f"Error loading sample data: {str(e)}")
        return False

def validate_environment():
    """Validate that required environment variables and dependencies are available"""
    required_vars = ["OPENAI_API_KEY", "GROQ_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        return False, f"Missing environment variables: {', '.join(missing_vars)}"
    
    return True, "Environment validation successful"

def get_system_info():
    """Get system information for debugging"""
    info = {
        "python_version": os.sys.version,
        "current_directory": os.getcwd(),
        "environment_vars": {
            "OPENAI_API_KEY": "Set" if os.getenv("OPENAI_API_KEY") else "Not Set",
            "GROQ_API_KEY": "Set" if os.getenv("GROQ_API_KEY") else "Not Set",
            "LANGCHAIN_TRACING_V2": os.getenv("LANGCHAIN_TRACING_V2", "Not Set"),
            "LANGCHAIN_PROJECT": os.getenv("LANGCHAIN_PROJECT", "Not Set")
        }
    }
    return info