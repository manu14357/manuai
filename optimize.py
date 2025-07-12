#!/usr/bin/env python3
"""
ManuAI Performance Optimization Tool

Use this tool to apply performance optimizations to your ManuAI setup.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from manuai.database_optimizer import get_optimizer
from manuai.performance_config import (get_performance_config,
                                       optimize_for_development,
                                       optimize_for_production)


def show_current_config():
    """Show current configuration."""
    config = get_performance_config()
    
    print("🔧 Current ManuAI Performance Configuration")
    print("=" * 50)
    
    print("\n📊 Database Settings:")
    print(f"  Max Connections: {config.database.max_connections}")
    print(f"  Query Cache Size: {config.database.query_cache_size}")
    print(f"  Cache TTL: {config.database.query_cache_ttl}s")
    print(f"  SQLite Cache Size: {config.database.cache_size}")
    print(f"  Journal Mode: {config.database.journal_mode}")
    
    print("\n🤖 LLM Settings:")
    print(f"  Simple Query Threshold: {config.llm.simple_query_threshold}")
    print(f"  Max Iterations: {config.llm.max_iterations}")
    print(f"  Response Caching: {config.llm.enable_response_caching}")
    print(f"  Response Cache Size: {config.llm.response_cache_size}")
    
    print("\n⚡ System Settings:")
    print(f"  Max Concurrent Requests: {config.system.max_concurrent_requests}")
    print(f"  Auto Optimization: {config.system.enable_auto_optimization}")
    print(f"  Metrics Collection: {config.system.enable_metrics_collection}")


def show_performance_stats():
    """Show current performance statistics."""
    try:
        from manuai.database_optimizer import performance_stats
        
        print("\n📈 Current Performance Statistics")
        print("=" * 50)
        
        stats = performance_stats()
        print(f"  Cache Hit Rate: {stats['cache_hit_rate']}")
        print(f"  Total Queries: {stats['queries_executed']}")
        print(f"  Avg Query Time: {stats['avg_query_time']:.3f}s")
        print(f"  Cache Requests: {stats['total_cache_requests']}")
        print(f"  Cache Hits: {stats['cache_hits']}")
        print(f"  Cache Misses: {stats['cache_misses']}")
        
    except Exception as e:
        print(f"Could not retrieve performance stats: {e}")


def show_recommendations():
    """Show optimization recommendations."""
    config = get_performance_config()
    recommendations = config.get_optimization_recommendations()
    
    print("\n💡 Optimization Recommendations")
    print("=" * 50)
    
    has_recommendations = False
    for category, recs in recommendations.items():
        if recs:
            has_recommendations = True
            print(f"\n{category.upper()}:")
            for rec in recs:
                print(f"  ⚠️  {rec['setting']}")
                print(f"      Current: {rec['current']}")
                print(f"      Recommended: {rec['recommended']}")
                print(f"      Reason: {rec['reason']}")
    
    if not has_recommendations:
        print("\n✅ No optimization recommendations at this time.")
        print("Your configuration looks good!")


def apply_optimizations():
    """Apply automatic optimizations."""
    print("\n🚀 Applying Automatic Optimizations")
    print("=" * 50)
    
    config = get_performance_config()
    recommendations = config.get_optimization_recommendations()
    
    if any(recommendations.values()):
        config.apply_recommendations(recommendations)
        print("✅ Optimizations applied successfully!")
        print("Restart your ManuAI application to see the changes.")
    else:
        print("✅ No optimizations needed at this time.")


def benchmark_database():
    """Run a simple database benchmark."""
    print("\n🏃 Running Database Benchmark")
    print("=" * 50)
    
    try:
        import time

        from manuai.database_optimizer import cached_query

        # Test query performance
        test_queries = [
            "SELECT COUNT(*) FROM customers",
            "SELECT * FROM products LIMIT 10",
            "SELECT * FROM orders LIMIT 5",
            "SELECT COUNT(*) FROM order_items"
        ]
        
        total_time = 0
        for i, query in enumerate(test_queries, 1):
            print(f"  Running test {i}/4: {query[:30]}...")
            start = time.time()
            try:
                result = cached_query(query)
                end = time.time()
                elapsed = end - start
                total_time += elapsed
                print(f"    ✅ Completed in {elapsed:.3f}s ({len(result)} rows)")
            except Exception as e:
                print(f"    ❌ Failed: {e}")
        
        print(f"\n📊 Benchmark Results:")
        print(f"  Total Time: {total_time:.3f}s")
        print(f"  Average Time: {total_time/len(test_queries):.3f}s")
        
        if total_time < 1.0:
            print("  🚀 Performance: Excellent!")
        elif total_time < 3.0:
            print("  ⚡ Performance: Good")
        else:
            print("  ⚠️  Performance: Could be improved")
            
    except Exception as e:
        print(f"Benchmark failed: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="ManuAI Performance Optimization Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python optimize.py --show-config          # Show current configuration
  python optimize.py --show-stats           # Show performance statistics
  python optimize.py --recommendations      # Show optimization recommendations
  python optimize.py --apply                # Apply automatic optimizations
  python optimize.py --production           # Apply production optimizations
  python optimize.py --development          # Apply development optimizations
  python optimize.py --benchmark            # Run database benchmark
        """
    )
    
    parser.add_argument('--show-config', action='store_true',
                       help='Show current configuration')
    parser.add_argument('--show-stats', action='store_true',
                       help='Show performance statistics')
    parser.add_argument('--recommendations', action='store_true',
                       help='Show optimization recommendations')
    parser.add_argument('--apply', action='store_true',
                       help='Apply automatic optimizations')
    parser.add_argument('--production', action='store_true',
                       help='Apply production optimizations')
    parser.add_argument('--development', action='store_true',
                       help='Apply development optimizations')
    parser.add_argument('--benchmark', action='store_true',
                       help='Run database benchmark')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🧙‍♂️ ManuAI Performance Optimization Tool")
    print("=" * 50)
    
    if args.show_config:
        show_current_config()
    
    if args.show_stats:
        show_performance_stats()
    
    if args.recommendations:
        show_recommendations()
    
    if args.apply:
        apply_optimizations()
    
    if args.production:
        optimize_for_production()
    
    if args.development:
        optimize_for_development()
    
    if args.benchmark:
        benchmark_database()


if __name__ == "__main__":
    main()
