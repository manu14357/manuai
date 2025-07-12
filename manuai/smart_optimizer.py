"""
Smart Query Optimizer for Querymancer.

This module provides intelligent query optimization suggestions
and database-specific optimizations for better performance.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from manuai.database_optimizer import get_optimizer


@dataclass
class QueryOptimization:
    """Represents a query optimization suggestion."""
    original_query: str
    optimized_query: str
    optimization_type: str
    description: str
    estimated_improvement: str


class SmartQueryOptimizer:
    """Provides intelligent query optimization suggestions."""
    
    def __init__(self):
        self.optimizer = get_optimizer()
        self.common_patterns = self._load_optimization_patterns()
    
    def _load_optimization_patterns(self) -> Dict[str, Dict]:
        """Load common query optimization patterns."""
        return {
            "missing_limit": {
                "pattern": r"SELECT\s+.*?\s+FROM\s+\w+(?:\s+WHERE\s+.+)?(?:\s+ORDER\s+BY\s+.+)?$",
                "suggestion": "Consider adding LIMIT clause for large result sets",
                "fix": lambda q: f"{q} LIMIT 100" if "LIMIT" not in q.upper() else q
            },
            "inefficient_like": {
                "pattern": r"WHERE\s+\w+\s+LIKE\s+['\"]%.*?%['\"]",
                "suggestion": "LIKE with leading wildcard can be slow. Consider full-text search if available",
                "fix": lambda q: q  # No automatic fix for this one
            },
            "missing_index_hints": {
                "pattern": r"WHERE\s+(\w+)\s*=\s*['\"]?.*?['\"]?",
                "suggestion": "Consider creating index on frequently queried columns",
                "fix": lambda q: q  # No automatic fix
            },
            "select_star": {
                "pattern": r"SELECT\s+\*\s+FROM",
                "suggestion": "Consider selecting specific columns instead of * for better performance",
                "fix": lambda q: q  # Manual optimization needed
            }
        }
    
    def analyze_query(self, query: str) -> List[QueryOptimization]:
        """Analyze a query and provide optimization suggestions."""
        optimizations = []
        
        # Check for common patterns
        for pattern_name, pattern_info in self.common_patterns.items():
            if re.search(pattern_info["pattern"], query, re.IGNORECASE):
                optimized = pattern_info["fix"](query)
                if optimized != query:
                    optimizations.append(QueryOptimization(
                        original_query=query,
                        optimized_query=optimized,
                        optimization_type=pattern_name,
                        description=pattern_info["suggestion"],
                        estimated_improvement="Minor to Moderate"
                    ))
        
        # Check for table-specific optimizations
        table_optimizations = self._get_table_specific_optimizations(query)
        optimizations.extend(table_optimizations)
        
        return optimizations
    
    def _get_table_specific_optimizations(self, query: str) -> List[QueryOptimization]:
        """Get optimizations specific to the tables in the query."""
        optimizations = []
        
        # Extract table names from query
        table_pattern = r"FROM\s+(\w+)|JOIN\s+(\w+)"
        tables = []
        for match in re.finditer(table_pattern, query, re.IGNORECASE):
            table_name = match.group(1) or match.group(2)
            if table_name:
                tables.append(table_name)
        
        # Check if tables exist and get their stats
        for table in tables:
            try:
                # Get table info
                schema = self.optimizer.get_table_schema_cached(table)
                if schema:
                    # Check for large tables without LIMIT
                    row_count = self._estimate_table_size(table)
                    if row_count > 1000 and "LIMIT" not in query.upper():
                        optimizations.append(QueryOptimization(
                            original_query=query,
                            optimized_query=f"{query} LIMIT 100",
                            optimization_type="large_table_limit",
                            description=f"Table '{table}' has ~{row_count} rows. Adding LIMIT for better performance",
                            estimated_improvement="Significant"
                        ))
            except Exception:
                pass  # Skip if table doesn't exist
        
        return optimizations
    
    def _estimate_table_size(self, table_name: str) -> int:
        """Estimate the size of a table."""
        try:
            result = self.optimizer.execute_cached_query(f"SELECT COUNT(*) FROM {table_name}")
            return result[0][0] if result else 0
        except Exception:
            return 0
    
    def suggest_indexes(self, query: str) -> List[str]:
        """Suggest indexes that might improve query performance."""
        suggestions = []
        
        # Look for WHERE clauses
        where_pattern = r"WHERE\s+(\w+)\s*[=<>!]"
        for match in re.finditer(where_pattern, query, re.IGNORECASE):
            column = match.group(1)
            suggestions.append(f"CREATE INDEX IF NOT EXISTS idx_{column} ON table_name({column})")
        
        # Look for ORDER BY clauses
        order_pattern = r"ORDER\s+BY\s+(\w+)"
        for match in re.finditer(order_pattern, query, re.IGNORECASE):
            column = match.group(1)
            suggestions.append(f"CREATE INDEX IF NOT EXISTS idx_{column}_order ON table_name({column})")
        
        return suggestions
    
    def get_query_execution_plan(self, query: str) -> Optional[str]:
        """Get the execution plan for a query."""
        try:
            explain_query = f"EXPLAIN QUERY PLAN {query}"
            result = self.optimizer.execute_cached_query(explain_query)
            
            if result:
                plan_lines = []
                for row in result:
                    plan_lines.append(" | ".join(str(col) for col in row))
                return "\n".join(plan_lines)
        except Exception as e:
            return f"Could not get execution plan: {str(e)}"
        
        return None
    
    def optimize_for_common_patterns(self, user_query: str) -> Tuple[str, List[str]]:
        """Optimize user query and provide suggestions."""
        
        # Common query pattern optimizations
        optimized_query = user_query
        suggestions = []
        
        # Pattern 1: "Show me all X" -> Add LIMIT
        if re.search(r"show\s+me\s+all\s+", user_query, re.IGNORECASE):
            suggestions.append("Consider limiting results for better performance")
            optimized_query = f"{user_query} (suggest adding LIMIT)"
        
        # Pattern 2: "Find customers named X" -> Use indexed search
        if re.search(r"find\s+\w+\s+named\s+", user_query, re.IGNORECASE):
            suggestions.append("Using exact match for better performance")
        
        # Pattern 3: "Get details about X" -> Select specific columns
        if re.search(r"get\s+details\s+about\s+", user_query, re.IGNORECASE):
            suggestions.append("Will select specific columns for efficiency")
        
        return optimized_query, suggestions


# Global instance
_query_optimizer = None


def get_query_optimizer() -> SmartQueryOptimizer:
    """Get global query optimizer instance."""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = SmartQueryOptimizer()
    return _query_optimizer
