import streamlit as st
import re
from langchain_core.prompts import ChatPromptTemplate

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def check_special_characters(name: str) -> tuple:
    """Check if name contains prohibited special characters"""
    # Allowed characters: letters, numbers, spaces, and basic punctuation
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')
    
    # Add Arabic characters
    for i in range(0x0600, 0x06FF + 1):
        allowed_chars.add(chr(i))
    
    # Add French accented characters
    french_chars = 'àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸ'
    for char in french_chars:
        allowed_chars.add(char)
    
    # Basic allowed punctuation
    basic_punctuation = ".-'&"
    for char in basic_punctuation:
        allowed_chars.add(char)
    
    # Find special characters
    special_chars = []
    for char in name:
        if char not in allowed_chars:
            special_chars.append(char)
    
    if special_chars:
        return True, list(set(special_chars))  # Remove duplicates
    return False, []

def check_hate_words_similarity(text, hate_store, threshold=0.8):
    """Check for hate words using vector similarity"""
    if not hate_store or not text.strip():
        return []
    
    try:
        results = hate_store.similarity_search_with_score(text.lower(), k=5)
        hate_matches = []
        
        for doc, score in results:
            # Lower score means higher similarity in some embedding spaces
            similarity = max(0, 1 - score)  # Convert to 0-1 similarity
            if similarity >= threshold:
                hate_matches.append({
                    'word': doc.page_content.strip(),
                    'similarity': similarity,
                    'type': doc.metadata.get('type', 'unknown')
                })
        
        return hate_matches
    except Exception as e:
        st.error(f"Hate word check error: {str(e)}")
        return []

def check_business_similarity(business_name, companies_store):
    """Check similarity with existing business names"""
    if not companies_store or not business_name.strip():
        return {
            'status': 'ERROR',
            'reason': 'Invalid input or database unavailable',
            'matches': []
        }
    
    try:
        results_with_scores = companies_store.similarity_search_with_score(business_name, k=5)
        
        if not results_with_scores:
            return {
                'status': 'AVAILABLE',
                'reason': 'No similar names found',
                'matches': []
            }
        
        matches = []
        exact_found = False
        
        for doc, score in results_with_scores:
            content = doc.page_content
            ar_name = ""
            fr_name = ""
            doc_id = ""
            
            lines = content.split('\n')
            for line in lines:
                if 'NOM_AR:' in line:
                    ar_name = line.split('NOM_AR:')[1].strip()
                elif 'NOM_FR:' in line:
                    fr_name = line.split('NOM_FR:')[1].strip()
                elif 'ID:' in line:
                    doc_id = line.split('ID:')[1].strip()
            
            similarity_percent = max(0, min(100, (2 - score) * 50))
            
            matches.append({
                'id': doc_id,
                'arabic': ar_name,
                'french': fr_name,
                'score': score,
                'similarity': similarity_percent
            })
            
            input_lower = business_name.lower().strip()
            if (ar_name and ar_name.lower().strip() == input_lower) or \
               (fr_name and fr_name.lower().strip() == input_lower) or \
               score < 0.1:  # Very high similarity threshold
                exact_found = True
        
        if exact_found:
            status = 'NOT AVAILABLE'
            reason = 'Exact or very similar name found in database'
        elif matches and matches[0]['score'] < 0.3:
            status = 'HIGH RISK'
            reason = 'Very similar names exist in database'
        elif matches and matches[0]['score'] < 0.5:
            status = 'MEDIUM RISK'
            reason = 'Moderately similar names exist'
        else:
            status = 'AVAILABLE'
            reason = 'No significant similarities found'
        
        return {
            'status': status,
            'reason': reason,
            'matches': matches if status != 'AVAILABLE' else []
        }
        
    except Exception as e:
        return {
            'status': 'ERROR',
            'reason': f'Database error: {str(e)}',
            'matches': []
        }

def extract_business_name_from_query(query, llm):
    """Extract business name from conversational query"""
    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a business name extraction expert. Extract ONLY the business name from user queries.

Rules:
- If user asks about checking/verifying a name, extract that name
- If user provides just a name, return it as-is
- If no business name mentioned, return "NONE"
- Keep original language (Arabic/French/English)
- Remove quotes and question words only

Examples:
- "check if TechCorp is available" → "TechCorp"
- "هل اسم 'الشركة الذكية' متاح؟" → "الشركة الذكية"
- "I want to name my company BlueSky" → "BlueSky"
- "What makes a good business name?" → "NONE"
- "FilthyCode Inc" → "FilthyCode Inc"

Query: {query}
Business Name:"""),
        ("human", "{query}")
    ])
    
    try:
        chain = extraction_prompt | llm
        response = chain.invoke({"query": query})
        extracted = response.content.strip()
        
        if extracted == "NONE" or not extracted:
            return None
        
        # Clean extracted name
        extracted = re.sub(r'^["\']|["\']$', '', extracted)
        return extracted.strip()
    except:
        return None

def generate_alternatives(business_name, remove_special_chars=False):
    """Generate alternative business names"""
    if not business_name:
        return []
    
    alternatives = []
    
    # If removing special characters, clean the name first
    if remove_special_chars:
        # Remove special characters but keep basic punctuation
        cleaned_name = re.sub(r'[^a-zA-Z0-9\u0600-\u06FF\s.\-\'&àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸ]', '', business_name)
        base_name = cleaned_name.strip()
    else:
        base_name = business_name
    
    if not base_name:
        # If no valid base name, provide generic alternatives
        return ["TechSolutions", "SmartBusiness", "ProServices"]
    
    if any(char in base_name for char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        # English/French name
        alternatives = [
            f"{base_name} Plus",
            f"{base_name} Pro", 
            f"{base_name} Tunisia",
            f"New {base_name}",
            f"{base_name} Solutions"
        ]
    else:
        # Arabic name
        alternatives = [
            f"{base_name} الجديدة",
            f"{base_name} بلس",
            f"{base_name} تونس", 
            f"{base_name} المتطورة",
            f"مؤسسة {base_name}"
        ]
    
    return alternatives[:3]

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_business_name(business_name, companies_store, hate_store, llm):
    """Comprehensive business name analysis with special character detection"""
    if not business_name or not business_name.strip():
        return {
            'valid': False,
            'hate_words': [],
            'similarity_result': {'status': 'ERROR', 'reason': 'Empty name', 'matches': []},
            'alternatives': [],
            'special_chars': [],
            'has_special_chars': False
        }
    
    # Check for special characters FIRST (highest priority)
    has_special_chars, special_chars_list = check_special_characters(business_name)
    if has_special_chars:
        return {
            'valid': False,
            'hate_words': [],
            'similarity_result': {'status': 'BLOCKED', 'reason': 'Special characters not allowed', 'matches': []},
            'alternatives': generate_alternatives(business_name, remove_special_chars=True),
            'special_chars': special_chars_list,
            'has_special_chars': True
        }
    
    # Check for hate words
    hate_matches = check_hate_words_similarity(business_name, hate_store)
    
    # Check business name similarity
    similarity_result = check_business_similarity(business_name, companies_store)
    
    # Generate alternatives if needed
    alternatives = []
    if hate_matches or similarity_result['status'] in ['NOT AVAILABLE', 'HIGH RISK']:
        alternatives = generate_alternatives(business_name)
    
    return {
        'valid': len(hate_matches) == 0,
        'hate_words': hate_matches,
        'similarity_result': similarity_result,
        'alternatives': alternatives,
        'special_chars': [],
        'has_special_chars': False
    }

def display_analysis_results(business_name, analysis_result):
    """Display comprehensive analysis results with special character handling"""
    st.markdown(f"### 🎯 Analyzing: **{business_name}**")
    
    # Special characters check (highest priority)
    if analysis_result['has_special_chars']:
        special_chars_str = "', '".join(analysis_result['special_chars'])
        st.error("🔣 **SPECIAL CHARACTERS NOT ALLOWED**")
        
        st.markdown(f"""
        **❌ Detected characters:** `{special_chars_str}`
        
        **🚫 Issue:** Business names in Tunisia must contain only letters, numbers, spaces, and basic punctuation.
        
        **✅ Allowed characters:**
        - Letters: A-Z, a-z, Arabic letters (أ-ي)
        - Numbers: 0-9
        - Spaces and basic punctuation: `. - ' &`
        
        **❌ Not allowed:** `@ # $ % ^ * ( ) + = [ ] {{ }} | \\ : ; " < > ? / ~`
        
        **💡 Suggestion:** Remove special characters and use only standard business naming conventions.
        """)
        
        if analysis_result['alternatives']:
            st.markdown("#### 🔄 Suggested Clean Alternatives:")
            col1, col2, col3 = st.columns(3)
            for i, alt in enumerate(analysis_result['alternatives']):
                with [col1, col2, col3][i % 3]:
                    if st.button(f"✅ {alt}", key=f"special_alt_{i}", use_container_width=True):
                        return alt
        return None
    
    # Hate words check
    if analysis_result['hate_words']:
        st.error("🚫 **INAPPROPRIATE CONTENT DETECTED**")
        st.markdown("**Detected inappropriate words:**")
        for hate_match in analysis_result['hate_words']:
            st.error(f"• **{hate_match['word']}** (Type: {hate_match['type']}, Similarity: {hate_match['similarity']:.2%})")
        
        if analysis_result['alternatives']:
            st.markdown("#### 🔄 Suggested Clean Alternatives:")
            col1, col2, col3 = st.columns(3)
            for i, alt in enumerate(analysis_result['alternatives']):
                with [col1, col2, col3][i % 3]:
                    if st.button(f"✅ {alt}", key=f"hate_alt_{i}", use_container_width=True):
                        return alt
        return None
    
    # Business similarity check
    similarity_result = analysis_result['similarity_result']
    status = similarity_result['status']
    
    if status == 'AVAILABLE':
        st.success("🎉 **GREAT NEWS! Name is AVAILABLE**")
        st.markdown("""
        ✅ **No conflicts found in RNE database**
        ✅ **No similar names detected**  
        ✅ **Safe to proceed with registration**
        
        **Next Steps:**
        - 📋 Prepare required documents
        - 🏢 Submit application to RNE Tunisia
        - 💼 Begin business registration process
        """)
    
    elif status == 'NOT AVAILABLE':
        st.error("❌ **NAME NOT AVAILABLE**")
        st.markdown(f"**Reason:** {similarity_result['reason']}")
        
        if similarity_result['matches']:
            st.markdown("#### 📊 Conflicting Names:")
            for match in similarity_result['matches'][:3]:
                with st.expander(f"ID: {match['id']} - Similarity: {match['similarity']:.1f}%"):
                    if match['arabic']:
                        st.write(f"🇹🇳 Arabic: {match['arabic']}")
                    if match['french']:
                        st.write(f"🇫🇷 French: {match['french']}")
        
        if analysis_result['alternatives']:
            st.markdown("#### 🔄 Suggested Alternatives:")
            col1, col2, col3 = st.columns(3)
            for i, alt in enumerate(analysis_result['alternatives']):
                with [col1, col2, col3][i % 3]:
                    if st.button(f"✅ {alt}", key=f"sim_alt_{i}", use_container_width=True):
                        return alt
    
    elif status == 'HIGH RISK':
        st.error("⚠️ **HIGH RISK - SIMILAR NAMES EXIST**")
        st.markdown(f"**Reason:** {similarity_result['reason']}")
        st.markdown("**Recommendation:** Choose a different name to avoid legal issues.")
        
        if analysis_result['alternatives']:
            st.markdown("#### 🔄 Suggested Alternatives:")
            col1, col2, col3 = st.columns(3)
            for i, alt in enumerate(analysis_result['alternatives']):
                with [col1, col2, col3][i % 3]:
                    if st.button(f"✅ {alt}", key=f"risk_alt_{i}", use_container_width=True):
                        return alt
    
    elif status == 'MEDIUM RISK':
        st.warning("⚠️ **MEDIUM RISK - PROCEED WITH CAUTION**")
        st.markdown(f"**Reason:** {similarity_result['reason']}")
        st.markdown("""
        **Considerations:**
        - 🔍 Legal review recommended
        - ⚖️ Potential trademark conflicts
        - 📞 Consult with business attorney
        """)
    
    else:
        st.error(f"❌ **ERROR:** {similarity_result['reason']}")
    
    return None