"""
Performance monitoring dashboard for Querymancer.

This module provides real-time performance monitoring and 
optimization suggestions for the database-LLM integration.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from manuai.config import Config
from manuai.database_optimizer import get_optimizer, performance_stats
from manuai.smart_optimizer import get_query_optimizer


class PerformanceDashboard:
    """Dashboard for monitoring database and LLM performance."""
    
    def __init__(self):
        self.optimizer = get_optimizer()
        self.query_optimizer = get_query_optimizer()
    
    def render_performance_metrics(self):
        """Render performance metrics in Streamlit."""
        st.subheader("🚀 Performance Metrics")
        
        # Get current stats
        stats = performance_stats()
        
        # Create metrics columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Cache Hit Rate",
                value=stats['cache_hit_rate'],
                delta=None,
                help="Percentage of queries served from cache"
            )
        
        with col2:
            st.metric(
                label="Queries Executed",
                value=stats['queries_executed'],
                delta=None,
                help="Total number of database queries executed"
            )
        
        with col3:
            st.metric(
                label="Avg Query Time",
                value=f"{stats['avg_query_time']:.3f}s",
                delta=None,
                help="Average query execution time"
            )
        
        with col4:
            st.metric(
                label="Cache Requests",
                value=stats['total_cache_requests'],
                delta=None,
                help="Total cache requests made"
            )
        
        # Performance chart
        if stats['queries_executed'] > 0:
            self._render_performance_chart(stats)
    
    def _render_performance_chart(self, stats: Dict[str, Any]):
        """Render performance visualization chart."""
        
        # Create cache performance chart
        cache_data = {
            'Type': ['Cache Hits', 'Cache Misses'],
            'Count': [stats['cache_hits'], stats['cache_misses']]
        }
        
        fig = px.pie(
            cache_data,
            values='Count',
            names='Type',
            title='Cache Performance Distribution',
            color_discrete_map={
                'Cache Hits': '#2E8B57',
                'Cache Misses': '#DC143C'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_optimization_suggestions(self):
        """Render optimization suggestions."""
        st.subheader("💡 Optimization Suggestions")
        
        # Get current stats for analysis
        stats = performance_stats()
        suggestions = []
        
        # Analyze performance and provide suggestions
        if stats['cache_hit_rate'] == '0.0%' and stats['queries_executed'] > 0:
            suggestions.append({
                'type': 'warning',
                'title': 'Low Cache Hit Rate',
                'description': 'Consider enabling query caching or check if queries are properly cacheable.',
                'action': 'Review query patterns and enable caching where appropriate.'
            })
        
        if stats['avg_query_time'] > 1.0:
            suggestions.append({
                'type': 'warning',
                'title': 'Slow Query Performance',
                'description': f'Average query time is {stats["avg_query_time"]:.3f}s which is above optimal.',
                'action': 'Consider adding indexes or optimizing query structure.'
            })
        
        if stats['cache_hit_rate'] not in ['0.0%', '100.0%']:
            hit_rate = float(stats['cache_hit_rate'].rstrip('%'))
            if hit_rate > 80:
                suggestions.append({
                    'type': 'success',
                    'title': 'Excellent Cache Performance',
                    'description': f'Cache hit rate of {stats["cache_hit_rate"]} is excellent.',
                    'action': 'Keep up the good work!'
                })
        
        if not suggestions:
            suggestions.append({
                'type': 'info',
                'title': 'Performance Looking Good',
                'description': 'No immediate optimization suggestions available.',
                'action': 'Continue monitoring performance metrics.'
            })
        
        # Display suggestions
        for suggestion in suggestions:
            if suggestion['type'] == 'success':
                st.success(f"✅ **{suggestion['title']}**\n\n{suggestion['description']}\n\n*Action:* {suggestion['action']}")
            elif suggestion['type'] == 'warning':
                st.warning(f"⚠️ **{suggestion['title']}**\n\n{suggestion['description']}\n\n*Action:* {suggestion['action']}")
            else:
                st.info(f"ℹ️ **{suggestion['title']}**\n\n{suggestion['description']}\n\n*Action:* {suggestion['action']}")
    
    def render_database_health(self):
        """Render database health metrics."""
        st.subheader("🏥 Database Health")
        
        try:
            # Get database tables and their stats
            tables = self.optimizer.get_all_tables_cached()
            
            if tables:
                table_info = []
                for table in tables:
                    try:
                        # Get row count
                        count_result = self.optimizer.execute_cached_query(f"SELECT COUNT(*) FROM {table}")
                        row_count = count_result[0][0] if count_result else 0
                        
                        # Get schema info
                        schema = self.optimizer.get_table_schema_cached(table)
                        column_count = len(schema) if schema else 0
                        
                        table_info.append({
                            'Table': table,
                            'Rows': row_count,
                            'Columns': column_count,
                            'Status': '✅ Healthy' if row_count > 0 else '⚠️ Empty'
                        })
                    except Exception as e:
                        table_info.append({
                            'Table': table,
                            'Rows': 'Error',
                            'Columns': 'Error',
                            'Status': f'❌ Error: {str(e)[:30]}...'
                        })
                
                # Display as DataFrame
                df = pd.DataFrame(table_info)
                st.dataframe(df, use_container_width=True)
                
                # Show table sizes chart
                if len(table_info) > 1:
                    valid_tables = [t for t in table_info if isinstance(t['Rows'], int)]
                    if valid_tables:
                        fig = px.bar(
                            valid_tables,
                            x='Table',
                            y='Rows',
                            title='Table Row Counts',
                            color='Rows',
                            color_continuous_scale='viridis'
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No tables found in the database.")
        
        except Exception as e:
            st.error(f"Error checking database health: {str(e)}")
    
    def render_cache_management(self):
        """Render cache management controls."""
        st.subheader("🗄️ Cache Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Query Cache", help="Clear all cached query results"):
                self.optimizer.clear_caches()
                st.success("Query cache cleared!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("Refresh Stats", help="Refresh all performance statistics"):
                st.success("Stats refreshed!")
                time.sleep(1)
                st.rerun()
        
        # Cache size info
        stats = performance_stats()
        if stats['total_cache_requests'] > 0:
            st.info(f"Cache has handled {stats['total_cache_requests']} requests with {stats['cache_hit_rate']} hit rate")
    
    def render_query_analyzer(self):
        """Render query analysis tool."""
        st.subheader("🔍 Query Analyzer")
        
        # Query input
        query = st.text_area(
            "Enter SQL query to analyze:",
            placeholder="SELECT * FROM customers WHERE name = 'John'",
            height=100
        )
        
        if query.strip():
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Analyze Query"):
                    optimizations = self.query_optimizer.analyze_query(query)
                    
                    if optimizations:
                        st.subheader("Optimization Suggestions:")
                        for i, opt in enumerate(optimizations, 1):
                            with st.expander(f"Suggestion {i}: {opt.optimization_type}"):
                                st.write(f"**Description:** {opt.description}")
                                st.write(f"**Estimated Improvement:** {opt.estimated_improvement}")
                                if opt.optimized_query != opt.original_query:
                                    st.code(opt.optimized_query, language='sql')
                    else:
                        st.success("Query looks good! No optimization suggestions.")
            
            with col2:
                if st.button("Get Execution Plan"):
                    plan = self.query_optimizer.get_query_execution_plan(query)
                    if plan:
                        st.subheader("Execution Plan:")
                        st.code(plan, language='text')
                    else:
                        st.error("Could not retrieve execution plan.")


def render_business_intelligence_dashboard():
    """Render business intelligence dashboard."""
    st.subheader("🏢 Business Intelligence Dashboard")
    
    try:
        from manuai.business_intelligence import get_business_summary

        # Get business summary
        summary = get_business_summary()
        
        if "error" in summary:
            st.error(f"Error loading business data: {summary['error']}")
            return
        
        # Key metrics
        if summary.get("key_metrics"):
            st.subheader("📊 Key Business Metrics")
            cols = st.columns(min(len(summary["key_metrics"]), 4))
            for i, metric in enumerate(summary["key_metrics"][:4]):
                with cols[i % 4]:
                    metric_parts = metric.split(": ")
                    if len(metric_parts) == 2:
                        st.metric(metric_parts[0], metric_parts[1])
                    else:
                        st.metric("Metric", metric)
        
        # Quick insights
        if summary.get("insights"):
            st.subheader("🔍 Quick Insights")
            for insight in summary["insights"]:
                st.info(f"💡 {insight}")
        
        # Recommendations
        if summary.get("recommendations"):
            st.subheader("💡 Business Recommendations")
            for i, rec in enumerate(summary["recommendations"], 1):
                st.success(f"{i}. {rec}")
        
        # Business question examples
        st.subheader("❓ Try These Business Questions")
        
        example_questions = [
            "What's our total revenue?",
            "How many customers do we have?",
            "Which products sell best?",
            "What's our average order value?",
            "Who are our top customers?",
            "How is our business growing?",
            "What's our inventory status?",
            "How many orders do we process daily?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(example_questions):
            with cols[i % 2]:
                if st.button(question, key=f"biz_q_{i}"):
                    st.session_state.business_question = question
                    st.rerun()
        
        # Business question analyzer
        st.subheader("🔍 Business Question Analyzer")
        
        question = st.text_input(
            "Ask a business question:",
            placeholder="e.g., What's our total revenue this month?",
            value=st.session_state.get("business_question", "")
        )
        
        if question:
            with st.spinner("Analyzing business question..."):
                try:
                    from manuai.business_intelligence import \
                        analyze_business_question
                    
                    insight = analyze_business_question(question)
                    
                    # Display results
                    st.subheader(f"📊 {insight.title}")
                    st.write(insight.description)
                    
                    # Metrics
                    if insight.metrics:
                        st.subheader("📈 Key Metrics")
                        metric_cols = st.columns(min(len(insight.metrics), 3))
                        for i, metric in enumerate(insight.metrics):
                            with metric_cols[i % 3]:
                                st.metric(
                                    metric.name,
                                    metric.value,
                                    help=metric.description
                                )
                    
                    # Recommendations
                    if insight.recommendations:
                        st.subheader("💡 Recommendations")
                        for i, rec in enumerate(insight.recommendations, 1):
                            st.info(f"{i}. {rec}")
                    
                    # Confidence
                    st.subheader("🎯 Analysis Confidence")
                    st.progress(insight.confidence)
                    st.write(f"Confidence Level: {insight.confidence:.1%}")
                    
                except Exception as e:
                    st.error(f"Error analyzing business question: {str(e)}")
        
        # Clear session state
        if st.button("Clear Question"):
            if "business_question" in st.session_state:
                del st.session_state["business_question"]
            st.rerun()
    
    except Exception as e:
        st.error(f"Error loading business intelligence: {str(e)}")


def render_performance_dashboard():
    """Render the complete performance dashboard."""
    dashboard = PerformanceDashboard()
    
    # Create tabs for different sections
    tabs = st.tabs(["📊 Metrics", "💡 Optimization", "🏥 Database Health", "🗄️ Cache", "🔍 Query Analyzer", "🏢 Business Intelligence"])
    
    with tabs[0]:
        dashboard.render_performance_metrics()
    
    with tabs[1]:
        dashboard.render_optimization_suggestions()
    
    with tabs[2]:
        dashboard.render_database_health()
    
    with tabs[3]:
        dashboard.render_cache_management()
    
    with tabs[4]:
        dashboard.render_query_analyzer()
    
    with tabs[5]:
        render_business_intelligence_dashboard()
