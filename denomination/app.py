import streamlit as st
import os
from langchain_core.tracers.context import collect_runs
from langsmith import Client
from streamlit_feedback import streamlit_feedback
from utils import get_business_name_chain, initialize_vector_stores
from business_validator import (
    extract_business_name_from_query, 
    analyze_business_name, 
    display_analysis_results
)

# ============================================================================
# LANGSMITH CONFIGURATION
# ============================================================================
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = st.secrets.get("LANGSMITH_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = "legal-rne"

client = Client()

# ============================================================================
# CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Business Name Checker - Tunisia RNE",
    page_icon="🏢",
    layout="wide"
)

# ============================================================================
# INITIALIZE COMPONENTS
# ============================================================================
@st.cache_resource
def initialize_components():
    """Initialize all components including vector stores"""
    try:
        openai_key = st.secrets.get("OPENAI_API_KEY")
        groq_key = st.secrets.get("GROQ_API_KEY")
        
        if not openai_key or not groq_key:
            return None, None, None, False
        
        # Initialize vector stores (companies and hate words)
        companies_store, hate_store = initialize_vector_stores(openai_key)
        
        # Initialize LLM
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            temperature=0.1,
            model="llama-3.3-70b-versatile",
            api_key=groq_key,
            verbose=False,
            max_retries=2,
        )
        
        return companies_store, hate_store, llm, True
    except Exception as e:
        st.error(f"Initialization error: {str(e)}")
        return None, None, None, False

def render_sidebar(companies_store, hate_store):
    """Render the sidebar with status and controls"""
    with st.sidebar:
        st.header("📊 System Status")
        try:
            company_count = companies_store._collection.count() if companies_store else 0
            hate_count = hate_store._collection.count() if hate_store else 0
            st.success(f"🏢 Companies: {company_count:,}")
            st.success(f"🛡️ Hate words: {hate_count:,}")
        except:
            st.error("📊 Database connection failed")
        
        st.markdown("---")
        st.markdown("### 🔣 Validation Rules")
        st.markdown("""
        **✅ Allowed in business names:**
        - Letters (A-Z, a-z, Arabic)
        - Numbers (0-9)
        - Spaces
        - Basic punctuation: `. - ' &`
        
        **❌ Not allowed:**
        - Special characters: `@ # $ % ^ * ( ) + = [ ] { } | \\ : ; " < > ? / ~`
        - Inappropriate content
        - Exact duplicates
        """)
        
        st.markdown("---")
        st.markdown("### 💬 Feedback")
        feedback_option = "thumbs" if st.toggle("👍👎 / 😀😞", value=True) else "faces"
        
        st.markdown("---")
        st.markdown("### 🎯 Quick Tests")
        st.caption("Try these examples:")
        
        test_queries = {}
        if st.button("✅ Valid Name", key="test_valid", use_container_width=True):
            test_queries["valid"] = "Is TechSolutions available?"
        
        if st.button("🔣 Special Characters", key="test_special", use_container_width=True):
            test_queries["special"] = "Check Tech@Solutions#2024"
        
        if st.button("🚫 Inappropriate", key="test_inappropriate", use_container_width=True):
            test_queries["inappropriate"] = "BadWordTech available?"
        
        return feedback_option, test_queries

def handle_test_query(test_query, companies_store, hate_store, llm):
    """Handle test query processing"""
    st.session_state.messages.append({"role": "user", "content": test_query})
    
    with st.chat_message("assistant", avatar="🤖"):
        business_name = extract_business_name_from_query(test_query, llm)
        if business_name:
            analysis_result = analyze_business_name(business_name, companies_store, hate_store, llm)
            alternative_to_check = display_analysis_results(business_name, analysis_result)
            
            if alternative_to_check:
                st.session_state.check_alternative = alternative_to_check
                st.rerun()
            
            response_content = f"Analyzed business name: {business_name}"
        else:
            response_content = "Test query processed"
            st.markdown(response_content)
    
    st.session_state.messages.append({"role": "assistant", "content": response_content})

def handle_user_input(prompt, companies_store, hate_store, llm):
    """Handle user input and generate response"""
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🤖"):
        with collect_runs() as cb:
            business_name = extract_business_name_from_query(prompt, llm)
            
            if business_name:
                analysis_result = analyze_business_name(business_name, companies_store, hate_store, llm)
                alternative_to_check = display_analysis_results(business_name, analysis_result)
                
                if alternative_to_check:
                    st.session_state.check_alternative = alternative_to_check
                    st.rerun()
                
                response_content = f"Analyzed business name: {business_name}"
            else:
                try:
                    chain = get_business_name_chain(llm, companies_store)
                    response = chain.invoke({"query": prompt})
                    response_content = response.content if hasattr(response, 'content') else str(response)
                    st.markdown(response_content)
                except Exception as e:
                    response_content = f"""I'm here to help with business name validation! 

You can:
- **Check a specific name**: "Is TechCorp available?"
- **Ask for advice**: "What makes a good business name?"
- **Get alternatives**: "Suggest names for a tech startup"
- **Learn about registration**: "How do I register in Tunisia?"

**⚠️ Remember:** Business names cannot contain special characters like @ # $ % ^ * ( ) + = [ ] {{ }} | \\ : ; " < > ? / ~

What would you like to know?"""
                    st.markdown(response_content)
        
        if cb.traced_runs:
            st.session_state.run_id = cb.traced_runs[0].id
    
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_content
    })

def handle_feedback(feedback_option):
    """Handle user feedback submission"""
    if st.session_state.get("run_id"):
        run_id = st.session_state.run_id
        feedback = streamlit_feedback(
            feedback_type=feedback_option,
            optional_text_label="💬 [Optional] Please share your thoughts",
            key=f"feedback_{run_id}",
        )

        score_mappings = {
            "thumbs": {"👍": 1, "👎": 0},
            "faces": {"😀": 1, "🙂": 0.75, "😐": 0.5, "🙁": 0.25, "😞": 0},
        }

        scores = score_mappings[feedback_option]

        if feedback:
            score = scores.get(feedback["score"])
            if score is not None:
                feedback_type_str = f"{feedback_option} {feedback['score']}"
                try:
                    feedback_record = client.create_feedback(
                        run_id,
                        feedback_type_str,
                        score=score,
                        comment=feedback.get("text"),
                    )
                    st.success("✅ Thank you for your feedback!")
                    st.session_state.feedback = {
                        "feedback_id": str(feedback_record.id),
                        "score": score,
                    }
                except Exception as e:
                    st.error(f"Feedback error: {str(e)}")

def initialize_chat_history():
    """Initialize chat history if not exists"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant", 
            "content": """مرحباً! 👋 أنا مساعدك الذكي للتحقق من توفر أسماء الشركات في تونس.

Hello! 👋 I'm your AI assistant for business name validation in Tunisia.

I can help you with:
🔍 **Check business name availability**
💡 **Suggest alternative names**  
📋 **Business naming advice**
⚖️ **RNE registration guidance**
🔣 **Validate naming rules compliance**

**How can I help you today?**"""
        })

def main():
    """Main application function"""
    # Header
    st.title("🏢 Business Name Checker AI Assistant")
    st.markdown("### 🤖 Intelligent Business Name Validation for Tunisia RNE")
    
    # Initialize components
    companies_store, hate_store, llm, components_loaded = initialize_components()
    
    if not components_loaded:
        st.error("❌ Failed to initialize components. Please check your configuration.")
        st.stop()
    
    # Render sidebar and get controls
    feedback_option, test_queries = render_sidebar(companies_store, hate_store)
    
    # Handle test queries
    for test_type, test_query in test_queries.items():
        handle_test_query(test_query, companies_store, hate_store, llm)
        st.rerun()
    
    # Initialize chat history
    initialize_chat_history()
    
    # Display chat history
    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    
    # Handle chat input
    if prompt := st.chat_input("Ask me about business names, or tell me a name to check..."):
        handle_user_input(prompt, companies_store, hate_store, llm)
    
    # Handle alternative checking
    if 'check_alternative' in st.session_state:
        alternative = st.session_state.check_alternative
        del st.session_state.check_alternative
        
        st.session_state.messages.append({"role": "user", "content": f"Check: {alternative}"})
        with st.chat_message("assistant", avatar="🤖"):
            analysis_result = analyze_business_name(alternative, companies_store, hate_store, llm)
            display_analysis_results(alternative, analysis_result)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Checked alternative: {alternative}"
        })
    
    # Handle feedback
    handle_feedback(feedback_option)

if __name__ == "__main__":
    main()