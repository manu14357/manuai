"""
Database optimization module for faster LLM-database interactions.

This module provides:
1. Connection pooling for database performance
2. Query result caching
3. Schema caching to avoid repeated PRAGMA calls
4. Smart query optimization hints
"""

import hashlib
import json
import sqlite3
import threading
import time
from collections import OrderedDict
from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple

from manuai.config import Config


class DatabasePool:
    """Connection pool for SQLite database to improve performance."""
    
    def __init__(self, max_connections: int = 10, timeout: float = 30.0):
        self.max_connections = max_connections
        self.timeout = timeout
        self.pool = []
        self.in_use = set()
        self.lock = threading.RLock()
        self.created_connections = 0
        
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection from the pool."""
        with self.lock:
            # Try to get an existing connection
            if self.pool:
                conn = self.pool.pop()
                self.in_use.add(conn)
                return conn
            
            # Create new connection if under limit
            if self.created_connections < self.max_connections:
                conn = sqlite3.connect(
                    Config.Path.DATABASE_PATH,
                    timeout=self.timeout,
                    check_same_thread=False
                )
                # Enable optimizations
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA cache_size=10000")
                conn.execute("PRAGMA temp_store=MEMORY")
                
                self.created_connections += 1
                self.in_use.add(conn)
                return conn
            
            # Wait for a connection to be available
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                if self.pool:
                    conn = self.pool.pop()
                    self.in_use.add(conn)
                    return conn
                time.sleep(0.01)
            
            raise Exception("Database connection pool exhausted")
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool."""
        with self.lock:
            if conn in self.in_use:
                self.in_use.remove(conn)
                self.pool.append(conn)
    
    def close_all(self):
        """Close all connections in the pool."""
        with self.lock:
            for conn in self.pool:
                conn.close()
            for conn in self.in_use:
                conn.close()
            self.pool.clear()
            self.in_use.clear()
            self.created_connections = 0


class QueryResultCache:
    """Cache for database query results to avoid repeated execution."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.lock = threading.RLock()
    
    def _generate_key(self, query: str) -> str:
        """Generate cache key for query."""
        return hashlib.sha256(query.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[List[Tuple]]:
        """Get cached result for query."""
        key = self._generate_key(query)
        
        with self.lock:
            if key not in self.cache:
                return None
            
            timestamp, result = self.cache[key]
            
            # Check if expired
            if time.time() - timestamp > self.ttl:
                del self.cache[key]
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return result
    
    def set(self, query: str, result: List[Tuple]):
        """Cache query result."""
        key = self._generate_key(query)
        
        with self.lock:
            self.cache[key] = (time.time(), result)
            self.cache.move_to_end(key)
            
            # Trim if needed
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
    
    def clear(self):
        """Clear all cached results."""
        with self.lock:
            self.cache.clear()


class SchemaCache:
    """Cache for database schema information."""
    
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl
        self.lock = threading.RLock()
    
    def get_table_schema(self, table_name: str) -> Optional[List[Tuple]]:
        """Get cached table schema."""
        with self.lock:
            if table_name not in self.cache:
                return None
            
            timestamp, schema = self.cache[table_name]
            
            if time.time() - timestamp > self.ttl:
                del self.cache[table_name]
                return None
            
            return schema
    
    def set_table_schema(self, table_name: str, schema: List[Tuple]):
        """Cache table schema."""
        with self.lock:
            self.cache[table_name] = (time.time(), schema)
    
    def get_all_tables(self) -> Optional[List[str]]:
        """Get cached list of all tables."""
        with self.lock:
            if "_tables" not in self.cache:
                return None
            
            timestamp, tables = self.cache["_tables"]
            
            if time.time() - timestamp > self.ttl:
                del self.cache["_tables"]
                return None
            
            return tables
    
    def set_all_tables(self, tables: List[str]):
        """Cache list of all tables."""
        with self.lock:
            self.cache["_tables"] = (time.time(), tables)


class DatabaseOptimizer:
    """Main database optimizer with connection pooling and caching."""
    
    def __init__(self):
        self.pool = DatabasePool()
        self.query_cache = QueryResultCache()
        self.schema_cache = SchemaCache()
        self._stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "queries_executed": 0,
            "avg_query_time": 0.0
        }
    
    @contextmanager
    def get_cursor(self, readonly: bool = True):
        """Get optimized database cursor with connection pooling."""
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            if not readonly:
                conn.commit()
        except Exception:
            if not readonly:
                conn.rollback()
            raise
        finally:
            cursor.close()
            self.pool.return_connection(conn)
    
    def execute_cached_query(self, query: str) -> List[Tuple]:
        """Execute query with caching."""
        # Try cache first
        cached_result = self.query_cache.get(query)
        if cached_result is not None:
            self._stats["cache_hits"] += 1
            return cached_result
        
        # Execute query
        start_time = time.time()
        with self.get_cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        
        execution_time = time.time() - start_time
        
        # Update stats
        self._stats["cache_misses"] += 1
        self._stats["queries_executed"] += 1
        self._stats["avg_query_time"] = (
            (self._stats["avg_query_time"] * (self._stats["queries_executed"] - 1) + execution_time) 
            / self._stats["queries_executed"]
        )
        
        # Cache result (only cache SELECT queries)
        if query.strip().upper().startswith("SELECT"):
            self.query_cache.set(query, result)
        
        return result
    
    def get_table_schema_cached(self, table_name: str) -> List[Tuple]:
        """Get table schema with caching."""
        cached_schema = self.schema_cache.get_table_schema(table_name)
        if cached_schema is not None:
            return cached_schema
        
        with self.get_cursor() as cursor:
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            schema = cursor.fetchall()
        
        self.schema_cache.set_table_schema(table_name, schema)
        return schema
    
    def get_all_tables_cached(self) -> List[str]:
        """Get all tables with caching."""
        cached_tables = self.schema_cache.get_all_tables()
        if cached_tables is not None:
            return cached_tables
        
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cursor.fetchall()]
        
        self.schema_cache.set_all_tables(tables)
        return tables
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        cache_total = self._stats["cache_hits"] + self._stats["cache_misses"]
        hit_rate = (self._stats["cache_hits"] / cache_total * 100) if cache_total > 0 else 0
        
        return {
            **self._stats,
            "cache_hit_rate": f"{hit_rate:.1f}%",
            "total_cache_requests": cache_total
        }
    
    def clear_caches(self):
        """Clear all caches."""
        self.query_cache.clear()
        self.schema_cache.cache.clear()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.pool.close_all()


# Global optimizer instance
_optimizer = None
_optimizer_lock = threading.Lock()


def get_optimizer() -> DatabaseOptimizer:
    """Get global database optimizer instance."""
    global _optimizer
    if _optimizer is None:
        with _optimizer_lock:
            if _optimizer is None:
                _optimizer = DatabaseOptimizer()
    return _optimizer


def with_optimized_cursor(readonly: bool = True):
    """Context manager for optimized database cursor."""
    return get_optimizer().get_cursor(readonly=readonly)


def cached_query(query: str) -> List[Tuple]:
    """Execute query with caching."""
    return get_optimizer().execute_cached_query(query)


def performance_stats() -> Dict[str, Any]:
    """Get database performance statistics."""
    return get_optimizer().get_stats()
