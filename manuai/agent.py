import time
from datetime import datetime
from typing import List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from manuai.logging import green_border_style, log_panel
from manuai.tools import call_tool, get_available_tools

SYSTEM_PROMPT = f"""
You are ManuAI, an advanced AI assistant with dual capabilities: a business intelligence expert for database questions and a friendly conversation partner for casual chat.

🚨 CRITICAL INSTRUCTION: For casual greetings and simple conversations (like "hi", "hello", "how are you"), respond directly WITHOUT calling any tools or functions. For ANY question about data, database, or business information, you MUST use the appropriate database tools.

🚨 BUSINESS RULES - FOLLOW STRICTLY WHEN ANSWERING BUSINESS QUESTIONS:
1. NEVER make up, invent, or fabricate ANY data - EVER
2. ONLY return data that actually exists in the database
3. ALWAYS use the database tools to get real data for business questions
4. If a tool returns empty string "", that means NO DATA EXISTS - say so
5. NEVER show SQL code unless user specifically asks to see code
6. NEVER provide sample, example, or placeholder data without using tools
7. NEVER format responses as tables with made-up data
8. NEVER say things like "here's sample data" or create fake tables without using actual database tools
9. When users ask for "sample data", "order details", or any specific data, you MUST use the sample_table tool
10. ALWAYS call the appropriate database tools when users ask about data - no exceptions
11. ALWAYS format database results in a clear, professional manner with proper explanations
12. Provide context and insights about the data, not just raw results
13. When showing data, explain what each column represents and highlight key insights
14. Use proper formatting like tables or bullet points to make data readable
15. Always provide a comprehensive response that goes beyond just showing raw data

🧙‍♂️ PERSONALITY & CONVERSATIONAL ABILITIES:
- You are a friendly, helpful wizard-themed assistant
- For greetings and casual conversation, respond in a warm, personable manner
- Use light magical theming in casual conversations (e.g., "Greetings, seeker of knowledge!")
- Answer general questions to the best of your knowledge
- DO NOT use database tools for casual conversation, only for business queries
- DO NOT apologize for not using tools when they're not needed
- DO NOT format casual responses as JSON or database results

🎯 BUSINESS CAPABILITIES:
You can answer sophisticated business questions including:
- Revenue and sales analysis ("What's our total revenue?", "How much did we make last month?")
- Customer analytics ("Who are our top customers?", "How many customers do we have?")
- Product performance ("Which products sell best?", "What's our inventory status?")
- Business trends ("How is our business growing?", "What are the sales trends?")
- KPIs and metrics ("What's our average order value?", "How many orders do we process?")
- Strategic insights ("What should we focus on?", "Where are the opportunities?")

🎨 RESPONSE FORMATTING REQUIREMENTS:
- Always provide comprehensive, well-structured responses
- Use proper formatting (tables, bullet points, headers) for database results
- Explain what each piece of data means and provide business context
- Highlight key insights and patterns in the data
- Use clear section headers and organize information logically
- Make responses informative and actionable for business users
- Include data summaries and key takeaways when appropriate

🛠️ YOUR TOOLS (USE ONLY FOR BUSINESS/DATABASE QUESTIONS):
- list_tables: Get all table names in database
- describe_table: Get real table schema information
- sample_table: Get real sample rows from table
- execute_sql: Execute SQL queries and return ACTUAL database results
- get_db_stats: Get database performance statistics
- analyze_business_question_tool: Advanced business intelligence analysis

📊 INTELLIGENT QUERY DETECTION - CRITICAL FOR PROPER TOOL USAGE:

🔍 ALWAYS USE DATABASE TOOLS FOR THESE QUESTION TYPES:
- Any question about "the database" or "our database" or "database data"
- Questions about specific data ("what data do we have?", "show me the data")
- Business metrics questions ("revenue", "sales", "customers", "products")
- Data exploration ("what's in the database?", "tell me about the data")
- Table/schema questions ("what tables exist?", "database structure")
- Sample data requests ("show me some data", "what does the data look like", "give me sample data")
- Order details ("show me order details", "first 5 orders", "random orders")
- Customer data ("customer information", "customer details")
- Product data ("product information", "product details")
- Any request for specific database records or examples
- Database performance questions ("how's the database performing?")

💬 CASUAL CONVERSATION (NO TOOLS NEEDED - RESPOND DIRECTLY):
- Pure greetings ("hi", "hello", "how are you")
- General questions about you ("what are you doing?", "who are you?")
- Abstract concepts ("tell me about AI", "explain machine learning")
- Personal questions ("what's your favorite color?")

🚨 CRITICAL DETECTION RULES:
- If user mentions "database", "data", "tables", "records", "rows", "sample", "details", "information" → USE TOOLS
- If user asks about business metrics or specific information → USE TOOLS  
- If user wants to explore or understand what data exists → USE TOOLS
- If user asks for "sample data", "order details", "customer data", etc. → USE TOOLS
- If user asks to "show me", "give me", "display", "list" any data → USE TOOLS
- If user just wants to chat or asks general questions → DO NOT USE ANY TOOLS, RESPOND DIRECTLY
- When in doubt about data-related questions → USE TOOLS
- Only skip tools for pure casual conversation like "hi", "hello", "how are you"

⚠️ IMPORTANT: For casual conversations, DO NOT call any functions or tools. Simply respond directly with text.

✅ IMPROVED EXAMPLES:
User: "What's our total revenue?"
You: [Use analyze_business_question_tool] → Provide actual revenue with business context, trends, and insights

User: "tell me about the database"
You: [Use list_tables first, then describe key tables] → Show actual database structure with explanations

User: "what type of data is in the database?"
You: [Use list_tables and sample_table] → Show real data types, examples, and business context

User: "show me the first 5 rows in orders"
You: [Use sample_table with limit=5] → Present data in formatted table with column explanations and insights

User: "Hello, how are you today?"
You: "Greetings, noble questioner! I'm doing splendidly today, ready to assist with your queries!"

User: "What are you doing right now?"
You: "I'm here ready to help you explore your database or have a friendly chat!"

📋 RESPONSE STRUCTURE FOR DATABASE QUERIES:
1. **Data Overview**: Brief summary of what you're showing
2. **Formatted Results**: Clean tables or organized data presentation
3. **Column Explanations**: What each field represents
4. **Key Insights**: Notable patterns or important information
5. **Business Context**: How this data relates to business operations
6. **Next Steps**: Suggestions for further analysis (when appropriate)

🔥 ENHANCED BUSINESS INTELLIGENCE WORKFLOW:

🗂️ DATABASE EXPLORATION QUESTIONS:
"tell me about the database" → Use list_tables first, then describe_table for key tables
"what data do we have?" → Use list_tables + sample_table to show data examples
"what type of data is in the database?" → Use describe_table to show schemas and data types
"show me the database structure" → Use list_tables + describe_table for multiple tables

📊 BUSINESS ANALYSIS QUESTIONS:
"what's our revenue?" → Use analyze_business_question_tool for comprehensive insights
"who are our top customers?" → Use analyze_business_question_tool for customer analysis
"how is business performing?" → Use analyze_business_question_tool + get_db_stats

🔍 SPECIFIC DATA QUESTIONS:
"show me customer data" → Use sample_table to show real customer records
"what products do we sell?" → Use sample_table to show product information
"give me some order examples" → Use sample_table for order data

⚡ PERFORMANCE QUESTIONS:
"how's the database performing?" → Use get_db_stats for performance metrics
"database optimization status" → Use get_db_stats for optimization information

🎯 TOOL SELECTION LOGIC:
1. Database exploration → list_tables (always start here for "about database" questions)
2. Data structure/types → describe_table (for schema information)
3. Data examples → sample_table (for actual data samples)
4. Business insights → analyze_business_question_tool (for business questions)
5. Performance info → get_db_stats (for database performance)
6. Custom queries → execute_sql (for specific data requests)

Today is {datetime.now().strftime("%Y-%m-%d")}

REMEMBER: 
- Questions about "database" or "data" = USE TOOLS
- Start with list_tables for database exploration questions
- Use multiple tools in sequence for comprehensive answers
- Always provide well-formatted, professional responses with business context
- Explain data meanings and provide insights, not just raw results
- Use proper formatting (tables, headers, bullet points) for database responses
- Casual chat = NO TOOLS, RESPOND DIRECTLY
- When in doubt about data/database questions = USE TOOLS
- NEVER call functions for greetings like "hi", "hello", etc.
- Make every database response comprehensive and business-focused
""".strip()


def classify_query_type(query: str) -> tuple[str, str]:
    """
    Classify user query to determine if database tools should be used.
    Returns (query_type, reasoning)
    """
    query_lower = query.lower().strip()
    
    # Pure casual conversation keywords that should NOT trigger tools (very specific)
    pure_casual_keywords = [
        'hi', 'hello', 'hey', 'greetings', 'how are you', 'what are you doing',
        'who are you', 'your name', 'yourself', 'feeling', 'weather',
        'good morning', 'good afternoon', 'good evening', 'how\'s it going', 
        'what\'s up', 'sup', 'yo'
    ]
    
    # Check for pure casual conversation first (exact matches only)
    for keyword in pure_casual_keywords:
        if query_lower == keyword or query_lower.startswith(keyword + ' '):
            return "casual", f"Query is pure casual conversation: '{keyword}'"
    
    # Very short queries that are definitely casual
    if len(query_lower.split()) <= 2 and query_lower in ['hi', 'hello', 'hey', 'sup', 'yo']:
        return "casual", "Short greeting query"
    
    # Database-related keywords that should ALWAYS trigger tool usage
    database_keywords = [
        'database', 'data', 'table', 'tables', 'records', 'rows',
        'revenue', 'sales', 'customers', 'products', 'orders', 'metrics',
        'analytics', 'business', 'performance', 'statistics', 'stats',
        'total', 'count', 'sum', 'average', 'trend', 'analysis',
        'show me', 'what is', 'how much', 'how many', 'tell me about',
        'schema', 'structure', 'columns', 'fields', 'query', 'select',
        'sample', 'example', 'first', 'random', 'details', 'information',
        'give me', 'display', 'list', 'describe', 'explore'
    ]
    
    # Check for database-related content
    for keyword in database_keywords:
        if keyword in query_lower:
            return "database", f"Query contains database-related keyword: '{keyword}'"
    
    # Special patterns that indicate database queries
    database_patterns = [
        'about the data', 'what data', 'sample data', 'order details', 
        'customer data', 'product data', 'business data', 'in the database',
        'from the database', 'database contains', 'what\'s in', 'show data'
    ]
    
    for pattern in database_patterns:
        if pattern in query_lower:
            return "database", f"Query matches database pattern: '{pattern}'"
    
    # Any question asking for specific information likely needs database tools
    if any(word in query_lower for word in ['what', 'how', 'show', 'tell', 'list', 'describe', 'give']):
        return "database", "Informational query likely needs database tools"
    
    return "casual", "Default classification for unclear queries"


def create_history() -> List[BaseMessage]:
    return [SystemMessage(content=SYSTEM_PROMPT)]


def ask(
    query: str, history: List[BaseMessage], llm: BaseChatModel, max_iterations: int = 10
) -> str:
    log_panel(title="User Request", content=f"Query: {query}", border_style=green_border_style)

    # Classify query type for better tool usage
    query_type, classification_reasoning = classify_query_type(query)
    log_panel(
        title="Query Classification", 
        content=f"Type: {query_type.upper()}\nReasoning: {classification_reasoning}",
        border_style="cyan"
    )

    # Track performance
    start_time = time.time()
    tool_calls_made = 0

    # Always bind tools, but guide the model on when to use them
    tools = get_available_tools()
    llm_with_tools = llm.bind_tools(tools)

    n_iterations = 0
    messages = history.copy()
    
    # Add enhanced context to help the model understand query classification
    if query_type == "database":
        enhanced_query = f"""
Query: {query}

[SYSTEM DIRECTIVE: This is a DATABASE query. You MUST use the appropriate database tools to provide real data. 
Classification: {classification_reasoning}
REQUIRED ACTIONS: 
1. Use database tools (sample_table, list_tables, describe_table, etc.) to get actual data from the database
2. Format the response professionally with proper structure and explanations
3. Provide business context and insights about the data
4. Use tables, headers, and bullet points for clear presentation
5. Explain what each column/field represents
6. Highlight key patterns or insights in the data
7. Make the response comprehensive and actionable for business users
DO NOT provide any made-up or example data. Only return real database results with proper formatting and context.]
"""
    else:
        enhanced_query = f"""
Query: {query}

[SYSTEM CONTEXT: This is a CASUAL conversation query. 
{classification_reasoning}
REQUIRED ACTION: Respond conversationally without using any database tools or functions.]
"""
    
    messages.append(HumanMessage(content=enhanced_query))

    while n_iterations < max_iterations:
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            # Log performance metrics
            total_time = time.time() - start_time
            log_panel(
                title="Performance Metrics",
                content=f"Total time: {total_time:.3f}s | Tool calls: {tool_calls_made} | Iterations: {n_iterations + 1}",
                border_style="blue"
            )
            
            # Log response type for debugging
            log_panel(
                title="Response Summary",
                content=f"Query type: {query_type.upper()} | Tools used: {tool_calls_made > 0} | Response length: {len(response.content)} chars",
                border_style="green"
            )
            return response.content
        
        for tool_call in response.tool_calls:
            tool_calls_made += 1
            log_panel(
                title=f"Tool Call #{tool_calls_made}",
                content=f"Tool: {tool_call['name']}\nArgs: {tool_call['args']}",
                border_style="magenta"
            )
            response = call_tool(tool_call)
            messages.append(response)
        n_iterations += 1

    # Log timeout scenario
    total_time = time.time() - start_time
    log_panel(
        title="Performance Metrics (Timeout)",
        content=f"Total time: {total_time:.3f}s | Tool calls: {tool_calls_made} | Iterations: {n_iterations}",
        border_style="red"
    )

    raise RuntimeError(
        "Maximum number of iterations reached. Please try again with a different query."
    )


def ask_stream(
    query: str, history: List[BaseMessage], llm: BaseChatModel, max_iterations: int = 10
):
    """
    Streaming version of ask function that yields response chunks as they arrive.
    """
    log_panel(title="User Request", content=f"Query: {query}", border_style=green_border_style)

    # Classify query type for better tool usage
    query_type, classification_reasoning = classify_query_type(query)
    log_panel(
        title="Query Classification", 
        content=f"Type: {query_type.upper()}\nReasoning: {classification_reasoning}",
        border_style="cyan"
    )

    # Track performance
    start_time = time.time()
    tool_calls_made = 0

    # Always bind tools, but guide the model on when to use them
    tools = get_available_tools()
    llm_with_tools = llm.bind_tools(tools)

    n_iterations = 0
    messages = history.copy()
    
    # Add enhanced context to help the model understand query classification
    if query_type == "database":
        enhanced_query = f"""
Query: {query}

[SYSTEM DIRECTIVE: This is a DATABASE query. You MUST use the appropriate database tools to provide real data. 
Classification: {classification_reasoning}
REQUIRED ACTIONS: 
1. Use database tools (sample_table, list_tables, describe_table, etc.) to get actual data from the database
2. Format the response professionally with proper structure and explanations
3. Provide business context and insights about the data
4. Use tables, headers, and bullet points for clear presentation
5. Explain what each column/field represents
6. Highlight key patterns or insights in the data
7. Make the response comprehensive and actionable for business users
DO NOT provide any made-up or example data. Only return real database results with proper formatting and context.]
"""
    else:
        enhanced_query = f"""
Query: {query}

[SYSTEM CONTEXT: This is a CASUAL conversation query. 
{classification_reasoning}
REQUIRED ACTION: Respond conversationally without using any database tools or functions.]
"""
    
    messages.append(HumanMessage(content=enhanced_query))

    # DON'T signal streaming start here - let loading continue during tool calls

    while n_iterations < max_iterations:
        # First, check if we need to use tools by getting a non-streaming response
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        
        if not response.tool_calls:
            # No tool calls needed, now stream the final response
            # Signal that response streaming is about to begin (THIS is when loading should disappear)
            yield "🔄 STREAMING_START"
            
            # We need to regenerate the final response with streaming
            # Remove the last non-streaming response
            streaming_messages = messages[:-1]
            
            # Stream the response
            for chunk in llm_with_tools.stream(streaming_messages):
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
            
            # Log performance metrics
            total_time = time.time() - start_time
            log_panel(
                title="Performance Metrics",
                content=f"Total time: {total_time:.3f}s | Tool calls: {tool_calls_made} | Iterations: {n_iterations + 1}",
                border_style="blue"
            )
            
            # Log response type for debugging
            log_panel(
                title="Response Summary",
                content=f"Query type: {query_type.upper()} | Tools used: {tool_calls_made > 0}",
                border_style="green"
            )
            return
        
        # Handle tool calls (non-streaming) - loading continues during this phase
        for tool_call in response.tool_calls:
            tool_calls_made += 1
            log_panel(
                title=f"Tool Call #{tool_calls_made}",
                content=f"Tool: {tool_call['name']}\nArgs: {tool_call['args']}",
                border_style="magenta"
            )
            tool_response = call_tool(tool_call)
            messages.append(tool_response)
        n_iterations += 1

    # Log timeout scenario
    total_time = time.time() - start_time
    log_panel(
        title="Performance Metrics (Timeout)",
        content=f"Total time: {total_time:.3f}s | Tool calls: {tool_calls_made} | Iterations: {n_iterations}",
        border_style="red"
    )

    raise RuntimeError(
        "Maximum number of iterations reached. Please try again with a different query."
    )
