import sqlite3
from contextlib import contextmanager
from typing import Any, List

from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.messages.tool import ToolCall
from langchain_core.tools import BaseTool

from manuai.config import Config
from manuai.database_optimizer import (cached_query, get_optimizer,
                                       with_optimized_cursor)
from manuai.logging import log, log_panel

# Global variable to store the current database path for multi-database support
_current_database_path = None


def set_current_database(db_path: str):
    """Set the current database path for tools to use."""
    global _current_database_path
    _current_database_path = db_path


def get_current_database() -> str:
    """Get the current database path, default to Config.Path.DATABASE_PATH."""
    return _current_database_path or str(Config.Path.DATABASE_PATH)


def get_available_tools() -> List[BaseTool]:
    return [list_tables, sample_table, describe_table, execute_sql, get_db_stats, analyze_business_question_tool]


def call_tool(tool_call: ToolCall) -> Any:
    tools_by_name = {tool.name: tool for tool in get_available_tools()}
    tool = tools_by_name[tool_call["name"]]
    response = tool.invoke(tool_call["args"])
    return ToolMessage(content=response, tool_call_id=tool_call["id"])


@contextmanager
def with_sql_cursor(readonly=True, db_path=None):
    """Use optimized database cursor with connection pooling."""
    if db_path is None:
        db_path = get_current_database()
    
    # Always use direct SQLite connection for multi-database support
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


@tool(parse_docstring=True)
def list_tables(reasoning: str) -> str:
    """Lists all user-created tables in the database (excludes SQLite system tables).

    Args:
        reasoning: Detailed explanation of why you need to see all tables (relate to the user's query)

    Returns:
        String representation of a list containing all table names
    """
    log_panel(
        title="List Tables Tool",
        content=f"Reasoning: {reasoning}",
    )
    try:
        with with_sql_cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
        return str(tables)
    except Exception as e:
        log(f"[red]Error listing tables: {str(e)}[/red]")
        return f"Error listing tables: {str(e)}"


@tool(parse_docstring=True)
def sample_table(reasoning: str, table_name: str, row_sample_size: int) -> str:
    """Retrieves a small sample of rows to understand the data structure and content of a specific table.

    Args:
        reasoning: Detailed explanation of why you need to see sample data from this table
        table_name: Exact name of the table to sample (case-sensitive, no quotes needed)
        row_sample_size: Number of rows to retrieve (recommended: 3-5 rows for readability)

    Returns:
        String with one row per line, showing all columns for each row as tuples
    """
    log_panel(
        title="Sample Table Tool",
        content=f"Table: {table_name}\nRows: {row_sample_size}\nReasoning: {reasoning}",
    )
    try:
        query = f"SELECT * FROM {table_name} LIMIT {row_sample_size}"
        with with_sql_cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        return "\n".join([str(row) for row in rows])
    except Exception as e:
        log(f"[red]Error sampling table: {str(e)}[/red]")
        return f"Error sampling table: {str(e)}"


@tool(parse_docstring=True)
def describe_table(reasoning: str, table_name: str) -> str:
    """Returns detailed schema information about a table (columns, types, constraints).

    Args:
        reasoning: Detailed explanation of why you need to understand this table's structure
        table_name: Exact name of the table to describe (case-sensitive, no quotes needed)

    Returns:
        String containing table schema information
    """
    log_panel(
        title="Describe Table Tool",
        content=f"Table: {table_name}\nReasoning: {reasoning}",
    )
    try:
        with with_sql_cursor() as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
            rows = cursor.fetchall()
        return "\n".join([str(row) for row in rows])
    except Exception as e:
        log(f"[red]Error describing table: {str(e)}[/red]")
        return f"Error describing table: {str(e)}"


@tool(parse_docstring=True)
def execute_sql(reasoning: str, sql_query: str) -> str:
    """Executes SQL query and returns the result with caching for better performance.

    Args:
        reasoning: Explanation of why this query is being run
        sql_query: Complete, properly formatted SQL query

    Returns:
        String with query results, one row per line as tuples
    """
    log_panel(
        title="Execute SQL Tool",
        content=f"Query: {sql_query}\nReasoning: {reasoning}",
    )
    try:
        with with_sql_cursor() as cursor:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
        return "\n".join([str(row) for row in rows])
    except Exception as e:
        log(f"[red]Error running query: {str(e)}[/red]")
        return f"Error running query: {str(e)}"


@tool(parse_docstring=True)
def get_db_stats(reasoning: str) -> str:
    """Get database performance statistics including cache hit rates and query performance.

    Args:
        reasoning: Explanation of why you need performance statistics

    Returns:
        String with database performance metrics
    """
    log_panel(
        title="Database Performance Stats",
        content=f"Reasoning: {reasoning}",
    )
    try:
        from manuai.database_optimizer import performance_stats
        stats = performance_stats()
        
        result = []
        result.append(f"Database Performance Statistics:")
        result.append(f"- Cache Hit Rate: {stats['cache_hit_rate']}")
        result.append(f"- Total Cache Requests: {stats['total_cache_requests']}")
        result.append(f"- Queries Executed: {stats['queries_executed']}")
        result.append(f"- Average Query Time: {stats['avg_query_time']:.3f}s")
        result.append(f"- Cache Hits: {stats['cache_hits']}")
        result.append(f"- Cache Misses: {stats['cache_misses']}")
        
        return "\n".join(result)
    except Exception as e:
        log(f"[red]Error getting database stats: {str(e)}[/red]")
        return f"Error getting database stats: {str(e)}"


@tool(parse_docstring=True)
def analyze_business_question_tool(reasoning: str, business_question: str) -> str:
    """Analyze business questions and provide intelligent insights using database information.
    
    Use this tool for:
    - Revenue and sales analysis
    - Customer analytics and behavior
    - Product performance insights
    - Business trends and growth analysis
    - KPI calculations and business metrics
    - Strategic business recommendations

    Args:
        reasoning: Detailed explanation of why you're analyzing this business question
        business_question: The natural language business question to analyze (e.g., "What's our total revenue?", "Who are our top customers?", "Which products sell best?")

    Returns:
        String with comprehensive business intelligence insights, metrics, and recommendations
    """
    log_panel(
        title="Business Intelligence Analysis",
        content=f"Question: {business_question}\nReasoning: {reasoning}",
    )
    try:
        from manuai.business_intelligence import analyze_business_question
        
        insight = analyze_business_question(business_question)
        
        result = []
        result.append(f"📊 {insight.title}")
        result.append("=" * 50)
        result.append(f"\n🔍 Analysis: {insight.description}")
        result.append(f"📈 Confidence: {insight.confidence:.1%}")
        
        if insight.metrics:
            result.append(f"\n📋 Key Metrics:")
            for metric in insight.metrics:
                result.append(f"  • {metric.name}: {metric.value}")
                if metric.description:
                    result.append(f"    ({metric.description})")
        
        if insight.recommendations:
            result.append(f"\n💡 Recommendations:")
            for i, rec in enumerate(insight.recommendations, 1):
                result.append(f"  {i}. {rec}")
        
        return "\n".join(result)
        
    except Exception as e:
        log(f"[red]Error analyzing business question: {str(e)}[/red]")
        return f"Error analyzing business question: {str(e)}"
