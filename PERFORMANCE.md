# ManuAI Performance Optimization Guide

This guide covers all aspects of optimizing ManuAI for maximum performance with your database and LLM integration.

## 🚀 Quick Start Optimization

### 1. Apply Production Optimizations
```bash
# Apply production-ready settings
uv run python optimize.py --production

# Or apply development settings
uv run python optimize.py --development
```

### 2. Check Current Performance
```bash
# Show current configuration
uv run python optimize.py --show-config

# Show performance statistics
uv run python optimize.py --show-stats

# Run database benchmark
uv run python optimize.py --benchmark
```

## 🔧 Performance Features

### Database Optimizations
- **Connection Pooling**: Reuses database connections for better performance
- **Query Result Caching**: Caches frequent query results (configurable TTL)
- **Schema Caching**: Caches table schemas to avoid repeated PRAGMA calls
- **SQLite Optimizations**: WAL mode, memory temp storage, optimized cache sizes

### LLM Optimizations
- **Smart Model Routing**: Routes simple queries to faster models
- **Tool Binding**: Ensures LLM can efficiently use database tools
- **Response Caching**: Caches similar responses to avoid regeneration
- **Performance Monitoring**: Tracks tool calls, iterations, and response times

### System Optimizations
- **Concurrent Request Handling**: Manages multiple requests efficiently
- **Auto-optimization**: Automatically applies performance improvements
- **Metrics Collection**: Tracks performance metrics for analysis

## 📊 Performance Dashboard

The Streamlit app includes a comprehensive performance dashboard:

1. **📊 Metrics Tab**: Real-time performance metrics and charts
2. **💡 Optimization Tab**: Automatic optimization suggestions
3. **🏥 Database Health Tab**: Database table statistics and health
4. **🗄️ Cache Tab**: Cache management and statistics
5. **🔍 Query Analyzer Tab**: SQL query analysis and optimization

## ⚡ Performance Tuning

### Database Configuration
```python
# Adjust in manuai/performance_config.py
DatabaseOptimizationConfig:
    max_connections: 20          # For high-traffic applications
    query_cache_size: 2000       # Larger cache for better hit rates
    query_cache_ttl: 600         # Cache TTL in seconds
    cache_size: 20000            # SQLite cache pages
```

### LLM Configuration
```python
# Adjust in manuai/performance_config.py
LLMOptimizationConfig:
    simple_query_threshold: 0.2   # Lower = more queries to fast model
    max_iterations: 8             # Reduce for faster responses
    response_cache_size: 1000     # Larger response cache
    enable_response_caching: True # Always enable for production
```

### System Configuration
```python
# Adjust in manuai/performance_config.py
SystemOptimizationConfig:
    max_concurrent_requests: 10   # Higher for better throughput
    enable_auto_optimization: True # Auto-apply optimizations
    enable_metrics_collection: True # Track performance
```

## 🎯 Performance Tips

### For Fast Responses
1. **Use Query Caching**: Enable query result caching for repeated queries
2. **Optimize Query Complexity**: Use LIMIT clauses, avoid SELECT *
3. **Index Frequently Queried Columns**: Create indexes on WHERE clause columns
4. **Use Connection Pooling**: Reuse database connections

### For High Throughput
1. **Increase Connection Pool Size**: More concurrent database connections
2. **Enable Response Caching**: Cache LLM responses for similar queries
3. **Use Smart Model Routing**: Route simple queries to faster models
4. **Optimize System Resources**: Increase concurrent request limits

### For Development
1. **Enable Performance Logging**: Track query performance and bottlenecks
2. **Use Smaller Cache Sizes**: Reduce memory usage during development
3. **Enable Metrics Collection**: Monitor performance trends
4. **Use Query Analyzer**: Optimize SQL queries before deployment

## 📈 Performance Monitoring

### Real-time Metrics
- **Cache Hit Rate**: Percentage of queries served from cache
- **Average Query Time**: Mean database query execution time
- **Tool Call Efficiency**: Number of LLM tool calls per query
- **Response Time**: Total time from query to response

### Performance Alerts
The system automatically suggests optimizations when:
- Cache hit rate is low (< 50%)
- Average query time is high (> 1s)
- Too many tool calls per query (> 5)
- Memory usage is high

## 🔍 Query Optimization

### Automatic Optimizations
- **LIMIT Addition**: Automatically suggests LIMIT for large result sets
- **Index Suggestions**: Recommends indexes for frequently queried columns
- **Query Execution Plans**: Shows SQLite query execution plans
- **Pattern Recognition**: Identifies common query patterns for optimization

### Manual Optimizations
```sql
-- Instead of this:
SELECT * FROM customers WHERE name LIKE '%john%'

-- Use this:
SELECT id, first_name, last_name, email 
FROM customers 
WHERE first_name = 'John' 
LIMIT 10
```

## 🛠️ Advanced Configuration

### Environment Variables
```bash
# Set performance preferences
export MANUAI_DB_POOL_SIZE=20
export MANUAI_CACHE_SIZE=2000
export MANUAI_ENABLE_METRICS=true
```

### Custom Optimization
```python
from manuai.performance_config import get_performance_config

config = get_performance_config()
config.database.max_connections = 30
config.llm.response_cache_size = 1500
config.save_config()
```

## 📊 Benchmarking

### Built-in Benchmark
```bash
# Run comprehensive benchmark
uv run python optimize.py --benchmark

# Expected results:
# - Total Time: < 1.0s (Excellent)
# - Total Time: < 3.0s (Good)
# - Total Time: > 3.0s (Needs optimization)
```

### Custom Benchmarks
```python
from manuai.database_optimizer import cached_query
import time

# Test query performance
start = time.time()
result = cached_query("SELECT COUNT(*) FROM customers")
print(f"Query time: {time.time() - start:.3f}s")
```

## 🎛️ Production Deployment

### Recommended Production Settings
```bash
# Apply production optimizations
uv run python optimize.py --production

# Verify configuration
uv run python optimize.py --show-config
uv run python optimize.py --show-stats
```

### Production Checklist
- [ ] Connection pooling enabled (max_connections ≥ 20)
- [ ] Query caching enabled (cache_size ≥ 2000)
- [ ] Response caching enabled
- [ ] Auto-optimization enabled
- [ ] Metrics collection enabled
- [ ] Performance monitoring set up
- [ ] Benchmark results acceptable (< 1.0s total)

## 🚨 Troubleshooting

### Common Issues
1. **Slow Queries**: Check database indexes, use LIMIT clauses
2. **Low Cache Hit Rate**: Increase cache sizes, check query patterns
3. **High Memory Usage**: Reduce cache sizes, optimize queries
4. **Connection Timeouts**: Increase connection pool size

### Performance Debugging
```bash
# Check current performance
uv run python optimize.py --show-stats

# Get optimization recommendations
uv run python optimize.py --recommendations

# Apply automatic fixes
uv run python optimize.py --apply
```

## 📚 Additional Resources

- [SQLite Performance Tuning](https://sqlite.org/optoverview.html)
- [LangChain Performance Tips](https://python.langchain.com/docs/guides/performance)
- [Streamlit Performance](https://docs.streamlit.io/library/advanced-features/performance)

---

For more detailed configuration options, see `manuai/performance_config.py`.
For real-time monitoring, use the Performance Dashboard in the Streamlit app.
