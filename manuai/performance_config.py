"""
Performance optimization configuration for Querymancer.

This file contains all the tunable parameters for optimizing
the database-LLM integration performance.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class DatabaseOptimizationConfig:
    """Configuration for database optimization."""
    
    # Connection Pool Settings
    max_connections: int = 10
    connection_timeout: float = 30.0
    
    # Query Cache Settings
    query_cache_size: int = 1000
    query_cache_ttl: int = 300  # 5 minutes
    
    # Schema Cache Settings
    schema_cache_ttl: int = 3600  # 1 hour
    
    # SQLite Optimization Settings
    journal_mode: str = "WAL"
    synchronous: str = "NORMAL"
    cache_size: int = 10000
    temp_store: str = "MEMORY"
    
    # Performance Monitoring
    enable_performance_logging: bool = True
    log_slow_queries: bool = True
    slow_query_threshold: float = 1.0  # seconds


@dataclass
class LLMOptimizationConfig:
    """Configuration for LLM optimization."""
    
    # Model Selection
    simple_query_threshold: float = 0.25
    complex_query_threshold: float = 0.75
    
    # Response Generation
    max_iterations: int = 10
    tool_call_timeout: float = 30.0
    
    # Caching
    enable_response_caching: bool = True
    response_cache_size: int = 500
    response_cache_ttl: int = 900  # 15 minutes
    
    # Performance Monitoring
    track_model_performance: bool = True
    enable_complexity_analysis: bool = True


@dataclass
class SystemOptimizationConfig:
    """Configuration for system-level optimizations."""
    
    # Memory Management
    max_memory_usage: str = "1GB"
    gc_threshold: int = 1000
    
    # Concurrent Processing
    max_concurrent_requests: int = 5
    request_queue_size: int = 100
    
    # Monitoring
    enable_metrics_collection: bool = True
    metrics_retention_days: int = 7
    
    # Auto-optimization
    enable_auto_optimization: bool = True
    optimization_interval: int = 3600  # 1 hour


class PerformanceConfig:
    """Main performance configuration class."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "performance_config.json"
        
        # Default configurations
        self.database = DatabaseOptimizationConfig()
        self.llm = LLMOptimizationConfig()
        self.system = SystemOptimizationConfig()
        
        # Load from file if exists
        self.load_config()
    
    def load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                import json
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                # Update database config
                if 'database' in data:
                    for key, value in data['database'].items():
                        if hasattr(self.database, key):
                            setattr(self.database, key, value)
                
                # Update LLM config
                if 'llm' in data:
                    for key, value in data['llm'].items():
                        if hasattr(self.llm, key):
                            setattr(self.llm, key, value)
                
                # Update system config
                if 'system' in data:
                    for key, value in data['system'].items():
                        if hasattr(self.system, key):
                            setattr(self.system, key, value)
                            
            except Exception as e:
                print(f"Error loading performance config: {e}")
    
    def save_config(self):
        """Save configuration to file."""
        try:
            import json
            data = {
                'database': self.database.__dict__,
                'llm': self.llm.__dict__,
                'system': self.system.__dict__
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving performance config: {e}")
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get performance optimization recommendations."""
        recommendations = {
            'database': [],
            'llm': [],
            'system': []
        }
        
        # Database recommendations
        if self.database.query_cache_size < 1000:
            recommendations['database'].append({
                'setting': 'query_cache_size',
                'current': self.database.query_cache_size,
                'recommended': 1000,
                'reason': 'Larger cache improves performance for repeated queries'
            })
        
        if self.database.max_connections < 10:
            recommendations['database'].append({
                'setting': 'max_connections',
                'current': self.database.max_connections,
                'recommended': 10,
                'reason': 'More connections handle concurrent requests better'
            })
        
        # LLM recommendations
        if self.llm.simple_query_threshold > 0.3:
            recommendations['llm'].append({
                'setting': 'simple_query_threshold',
                'current': self.llm.simple_query_threshold,
                'recommended': 0.25,
                'reason': 'Lower threshold routes more queries to fast model'
            })
        
        if not self.llm.enable_response_caching:
            recommendations['llm'].append({
                'setting': 'enable_response_caching',
                'current': False,
                'recommended': True,
                'reason': 'Response caching significantly improves performance'
            })
        
        # System recommendations
        if self.system.max_concurrent_requests < 5:
            recommendations['system'].append({
                'setting': 'max_concurrent_requests',
                'current': self.system.max_concurrent_requests,
                'recommended': 5,
                'reason': 'Higher concurrency improves system throughput'
            })
        
        return recommendations
    
    def apply_recommendations(self, recommendations: Dict[str, Any]):
        """Apply optimization recommendations."""
        for category, recs in recommendations.items():
            config_obj = getattr(self, category)
            for rec in recs:
                setting = rec['setting']
                value = rec['recommended']
                if hasattr(config_obj, setting):
                    setattr(config_obj, setting, value)
        
        self.save_config()


# Global configuration instance
_performance_config = None


def get_performance_config() -> PerformanceConfig:
    """Get global performance configuration."""
    global _performance_config
    if _performance_config is None:
        _performance_config = PerformanceConfig()
    return _performance_config


def optimize_for_production():
    """Apply production-ready optimizations."""
    config = get_performance_config()
    
    # Production database settings
    config.database.max_connections = 20
    config.database.query_cache_size = 2000
    config.database.cache_size = 20000
    
    # Production LLM settings
    config.llm.enable_response_caching = True
    config.llm.response_cache_size = 1000
    config.llm.max_iterations = 8
    
    # Production system settings
    config.system.max_concurrent_requests = 10
    config.system.enable_auto_optimization = True
    
    config.save_config()
    print("✅ Production optimizations applied!")


def optimize_for_development():
    """Apply development-friendly optimizations."""
    config = get_performance_config()
    
    # Development database settings
    config.database.max_connections = 5
    config.database.query_cache_size = 500
    config.database.enable_performance_logging = True
    
    # Development LLM settings
    config.llm.track_model_performance = True
    config.llm.enable_complexity_analysis = True
    
    # Development system settings
    config.system.enable_metrics_collection = True
    config.system.max_concurrent_requests = 3
    
    config.save_config()
    print("✅ Development optimizations applied!")
