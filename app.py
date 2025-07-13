import json
import random
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from manuai.agent import ask, ask_stream, create_history
from manuai.config import Config
from manuai.models import create_llm
from manuai.optimizations import (DynamicComplexityRouter,
                                  optimize_query_execution)
from manuai.performance_dashboard import render_performance_dashboard
from manuai.smart_optimizer import get_query_optimizer
from manuai.tools import set_current_database, with_sql_cursor

load_dotenv()


@contextmanager
def with_multi_db_cursor(db_path: str):
    """Context manager for database connections with multiple database support."""
    conn = sqlite3.connect(db_path)
    try:
        # Enable optimizations
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        
        cursor = conn.cursor()
        yield cursor
    finally:
        conn.close()


LOADING_MESSAGES = [
    "Consulting the ancient tomes of SQL wisdom...",
    "Casting query spells on your database...",
    "Summoning data from the digital realms...",
    "Deciphering your request into database runes...",
    "Brewing a potion of perfect query syntax...",
    "Channeling the power of database magic...",
    "Translating your words into the language of tables...",
    "Waving my SQL wand to fetch your results...",
    "Performing database divination...",
    "Aligning the database stars for optimal results...",
    "Consulting with the database spirits...",
    "Transforming natural language into database incantations...",
    "Peering into the crystal ball of your database...",
    "Opening a portal to your data dimension...",
    "Enchanting your request with SQL magic...",
    "Invoking the ancient art of query optimization...",
    "Reading between the tables to find your answer...",
    "Conjuring insights from your database depths...",
    "Weaving a tapestry of joins and filters...",
    "Preparing a feast of data for your consideration...",
]


def get_model(query: str = None) -> BaseChatModel:
    """Get appropriate LLM based on query complexity.

    Args:
        query: The user's natural language query (if provided)

    Returns:
        BaseChatModel: Configured language model for the query
    """
    if not query:
        # Default model if no query provided
        return create_llm(Config.MODEL)

    # Initialize the complexity router
    complexity_router = DynamicComplexityRouter()

    # Determine the appropriate model based on query complexity
    return complexity_router.get_appropriate_model(query)


def load_css(css_file):
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(
    page_title="ManuAI",
    page_icon="🧙‍♂️",
)

# Apply CSS styling
try:
    load_css("assets/style.css")
except FileNotFoundError:
    st.write("CSS file not found, using default styling")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = create_history()

# Header and description
st.header("ManuAI")
st.subheader("Talk to your database using natural language")

# Create tabs for main interface, performance dashboard, and fine-tuning
main_tab, performance_tab, fine_tuning_tab = st.tabs(["🌟 Chat", "📊 Performance", "🔄 Fine-Tuning"])

with performance_tab:
    render_performance_dashboard()

with fine_tuning_tab:
    st.header("Database Fine-Tuning")
    st.markdown("""
    Fine-tune the database for optimal LLM interaction. This process will:
    - Analyze table schemas and optimize column data types
    - Create missing indexes for better query performance
    - Optimize text columns for token efficiency
    - Apply database-specific optimizations
    """)
    
    # Get available tables
    try:
        # Use the selected database from session state, or default to the main database
        db_path = getattr(st.session_state, 'selected_database', Config.Path.DATABASE_PATH)
        with with_multi_db_cursor(str(db_path)) as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            available_tables = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")
        available_tables = []
    
    # Table selection
    selected_tables = st.multiselect(
        "Select tables to fine-tune (leave empty to fine-tune all tables)",
        options=available_tables
    )
    
    # Fine-tune button
    if st.button("Start Fine-Tuning"):
        with st.spinner("Fine-tuning database..."):
            try:
                # Use the selected database from session state
                db_path = getattr(st.session_state, 'selected_database', Config.Path.DATABASE_PATH)
                tables_to_tune = selected_tables if selected_tables else None
                
                if tables_to_tune:
                    results = []
                    for table in tables_to_tune:
                        # Process one table at a time
                        with with_multi_db_cursor(str(db_path)) as cursor:
                            cursor.execute(f"PRAGMA table_info('{table}')")
                            columns = cursor.fetchall()
                            
                            cursor.execute(f"SELECT COUNT(*) FROM {table}")
                            row_count = cursor.fetchone()[0]
                            
                            # Create indexes on foreign keys
                            cursor.execute(f"PRAGMA foreign_key_list('{table}')")
                            foreign_keys = cursor.fetchall()
                            
                            cursor.execute(f"PRAGMA index_list('{table}')")
                            indexes = cursor.fetchall()
                        
                        improvements = []
                        # Create missing indexes
                        for fk in foreign_keys:
                            if len(fk) > 3 and fk[3] is not None:
                                fk_column = fk[3]
                                index_name = f"idx_{table}_{fk_column}".lower()
                                
                                try:
                                    with with_multi_db_cursor(str(db_path)) as cursor:
                                        cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({fk_column})")
                                        improvements.append(f"Added index on foreign key column '{fk_column}'")
                                except Exception as e:
                                    st.warning(f"Could not create index on {fk_column}: {str(e)}")
                        
                        # Analyze table for query planning
                        with with_multi_db_cursor(str(db_path)) as cursor:
                            cursor.execute(f"ANALYZE {table}")
                            improvements.append("Analyzed table for improved query planning")
                        
                        # Record results
                        results.append({
                            "table_name": table,
                            "column_count": len(columns),
                            "row_count": row_count,
                            "improvements": improvements,
                            "execution_time": 0.1,
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
                        })
                else:
                    # Use the fine_tune.py script directly using subprocess
                    import subprocess
                    subprocess.run(["python", "fine_tune.py"], check=True)
                    
                    # Get results from the file
                    history_path = Path(Config.Path.APP_HOME) / "logs" / "fine_tuning_history.json"
                    if history_path.exists():
                        with open(history_path, "r") as f:
                            history = json.load(f)
                            results = history[-4:]  # Get the last 4 results (assuming 4 tables)
                
                # Show results
                st.success(f"✅ Fine-tuning complete! Processed {len(results) if results else 0} tables.")
                
                # Display improvements
                for result in results:
                    table_name = result.get("table_name", "Unknown")
                    improvements = result.get("improvements", [])
                    if improvements:
                        with st.expander(f"Improvements for {table_name}"):
                            for improvement in improvements:
                                st.info(improvement)
            except Exception as e:
                st.error(f"Error during fine-tuning: {str(e)}")
    
    # Show fine-tuning history if available
    import json
    from pathlib import Path
    
    history_path = Path(Config.Path.APP_HOME) / "logs" / "fine_tuning_history.json"
    if history_path.exists():
        try:
            with open(history_path, "r") as f:
                history = json.load(f)
            
            if history:
                st.subheader("Fine-Tuning History")
                
                # Group by date
                import datetime
                from collections import defaultdict
                
                grouped_history = defaultdict(list)
                for entry in history:
                    try:
                        date = datetime.datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d")
                        grouped_history[date].append(entry)
                    except (ValueError, KeyError):
                        pass
                
                # Display history by date
                for date, entries in sorted(grouped_history.items(), reverse=True):
                    with st.expander(f"{date} ({len(entries)} tables)"):
                        for entry in entries:
                            st.write(f"**{entry['table_name']}** ({entry['row_count']} rows, {len(entry['improvements'])} improvements)")
                            if entry["improvements"]:
                                for improvement in entry["improvements"]:
                                    st.info(improvement)
        except (json.JSONDecodeError, FileNotFoundError):
            st.write("No fine-tuning history available")

with main_tab:
    # Database selection
    st.subheader("Database Selection")
    
    # Get available databases
    available_databases = {
        "E-commerce Database": Config.Path.DATABASE_PATH,
        "ArcOps Manufacturing (500 tables)": Config.Path.ARCOPS_500_DB,
        "ArcOps Manufacturing (200 tables)": Config.Path.ARCOPS_200_DB,
        "Fake Database": Config.Path.FAKE_DB,
        "Memory Database": Config.Path.MEMORY_DB,
    }
    
    # Filter to only show databases that exist
    existing_databases = {}
    for name, path in available_databases.items():
        if Path(path).exists():
            existing_databases[name] = path
    
    if not existing_databases:
        st.error("No databases found! Please generate databases first using the scripts in the bin/ directory.")
        st.stop()
    
    # Database selector
    selected_db_name = st.selectbox(
        "Select Database",
        options=list(existing_databases.keys()),
        index=0
    )
    
    selected_db_path = existing_databases[selected_db_name]
    
    # Store selected database in session state
    st.session_state.selected_database = selected_db_path
    
    # Set the current database for the tools to use
    set_current_database(str(selected_db_path))
    
    st.info(f"Currently using: **{selected_db_name}**")
    
    # Display DB tables
    with st.expander("Database Tables"):
        try:
            with with_multi_db_cursor(str(selected_db_path)) as cursor:
                # Get list of tables
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                tables = [row[0] for row in cursor.fetchall()]

                st.write("### Available Tables")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    st.write(f"- {table} ({count} rows)")
        except Exception as e:
            st.error(f"Error accessing database: {str(e)}")
            st.write("Please ensure the database file exists and is accessible.")

    # Chat interface
    for message in st.session_state.messages:
        if type(message) is SystemMessage:
            continue
        is_user = type(message) is HumanMessage
        avatar = "😇" if is_user else "😇"
        with st.chat_message("user" if is_user else "ai", avatar=avatar):
            st.markdown(message.content)

    # Get user input
    if prompt := st.chat_input("Type your message..."):
        with st.chat_message("user", avatar="😊"):
            st.session_state.messages.append(HumanMessage(prompt))
            st.markdown(prompt)
        with st.chat_message("ai", avatar="😇"):
            message_placeholder = st.empty()
            
            # Show loading message initially
            loading_message = message_placeholder.status(random.choice(LOADING_MESSAGES), state="running")

            # Get query optimization suggestions
            query_optimizer = get_query_optimizer()
            optimized_prompt, suggestions = query_optimizer.optimize_for_common_patterns(prompt)

            # Show optimization suggestions if any
            if suggestions:
                with st.expander("🚀 Query Optimization Suggestions"):
                    for suggestion in suggestions:
                        st.info(suggestion)

            # Optimize query execution using our pipeline
            optimized_query, model, optimized_history, model_params = optimize_query_execution(
                prompt, st.session_state.messages
            )

            # Stream the response
            response_text = ""
            streaming_started = False
            
            try:
                for chunk in ask_stream(optimized_query, optimized_history, model, max_iterations=10):
                    # Handle control signals
                    if chunk == "🔄 STREAMING_START":
                        # Hide loading message when actual streaming starts
                        if not streaming_started:
                            message_placeholder.empty()
                            streaming_started = True
                        continue
                    
                    # Clear loading message on first real content (fallback safety)
                    if not streaming_started:
                        message_placeholder.empty()
                        streaming_started = True
                    
                    # Add chunk to response
                    response_text += chunk
                    # Update the display with current text and a blinking cursor
                    message_placeholder.markdown(response_text + "▌")
                
                # Remove cursor when streaming is complete
                message_placeholder.markdown(response_text)
                
            except Exception as e:
                # Clear loading message on error
                if not streaming_started:
                    message_placeholder.empty()
                
                # Fallback to non-streaming if streaming fails
                st.warning("Streaming failed, using fallback response...")
                response_text = ask(optimized_query, optimized_history, model, max_iterations=10)
                message_placeholder.markdown(response_text)

        # Add response to chat history
        st.session_state.messages.append(AIMessage(response_text))
