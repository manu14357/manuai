"""
Business Intelligence module for Querymancer.

This module provides advanced analytics and business intelligence capabilities,
allowing the system to answer complex business questions using database information.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from manuai.database_optimizer import cached_query, get_optimizer


@dataclass
class BusinessMetric:
    """Represents a business metric with context."""
    name: str
    value: Any
    description: str
    category: str
    trend: Optional[str] = None
    comparison: Optional[str] = None


@dataclass
class BusinessInsight:
    """Represents a business insight derived from data."""
    title: str
    description: str
    metrics: List[BusinessMetric]
    recommendations: List[str]
    confidence: float


class BusinessIntelligenceEngine:
    """Advanced business intelligence engine for answering business questions."""
    
    def __init__(self):
        self.optimizer = get_optimizer()
        self.business_patterns = self._load_business_patterns()
        self.metric_cache = {}
    
    def _load_business_patterns(self) -> Dict[str, Dict]:
        """Load business question patterns and their corresponding queries."""
        return {
            # Revenue and Sales Patterns
            "revenue_total": {
                "patterns": [
                    r"what.*(?:total|overall).*revenue",
                    r"how much.*(?:money|revenue|sales).*made",
                    r"total.*(?:sales|revenue|income)"
                ],
                "queries": [
                    "SELECT SUM(total_amount) as total_revenue FROM orders WHERE status = 'completed'",
                    "SELECT SUM(oi.quantity * p.price) as total_revenue FROM order_items oi JOIN products p ON oi.product_id = p.id JOIN orders o ON oi.order_id = o.id WHERE o.status = 'completed'"
                ],
                "category": "revenue"
            },
            
            "revenue_period": {
                "patterns": [
                    r"revenue.*(?:last|past).*(?:month|week|year|day)",
                    r"sales.*(?:this|last).*(?:month|week|year|quarter)",
                    r"how much.*made.*(?:last|this).*(?:month|week|year)"
                ],
                "queries": [
                    "SELECT SUM(total_amount) as period_revenue FROM orders WHERE status = 'completed' AND created_at >= date('now', '-30 days')",
                    "SELECT SUM(total_amount) as period_revenue FROM orders WHERE status = 'completed' AND created_at >= date('now', '-7 days')",
                    "SELECT SUM(total_amount) as period_revenue FROM orders WHERE status = 'completed' AND created_at >= date('now', '-1 year')"
                ],
                "category": "revenue"
            },
            
            # Customer Analytics Patterns
            "customer_count": {
                "patterns": [
                    r"how many.*customers",
                    r"total.*(?:customers|users|clients)",
                    r"customer.*count"
                ],
                "queries": [
                    "SELECT COUNT(*) as customer_count FROM customers",
                    "SELECT COUNT(DISTINCT customer_id) as active_customers FROM orders"
                ],
                "category": "customers"
            },
            
            "top_customers": {
                "patterns": [
                    r"(?:top|best|biggest).*customers",
                    r"who.*(?:spend|spent).*most",
                    r"highest.*(?:spending|value).*customers"
                ],
                "queries": [
                    "SELECT c.first_name, c.last_name, SUM(o.total_amount) as total_spent FROM customers c JOIN orders o ON c.id = o.customer_id WHERE o.status = 'completed' GROUP BY c.id ORDER BY total_spent DESC LIMIT 10",
                    "SELECT c.first_name, c.last_name, COUNT(o.id) as order_count FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id ORDER BY order_count DESC LIMIT 10"
                ],
                "category": "customers"
            },
            
            # Product Analytics Patterns
            "product_performance": {
                "patterns": [
                    r"(?:best|top).*(?:selling|popular).*products",
                    r"most.*(?:sold|popular).*(?:products|items)",
                    r"product.*(?:performance|sales)"
                ],
                "queries": [
                    "SELECT p.name, SUM(oi.quantity) as total_sold FROM products p JOIN order_items oi ON p.id = oi.product_id JOIN orders o ON oi.order_id = o.id WHERE o.status = 'completed' GROUP BY p.id ORDER BY total_sold DESC LIMIT 10",
                    "SELECT p.name, SUM(oi.quantity * p.price) as revenue FROM products p JOIN order_items oi ON p.id = oi.product_id JOIN orders o ON oi.order_id = o.id WHERE o.status = 'completed' GROUP BY p.id ORDER BY revenue DESC LIMIT 10"
                ],
                "category": "products"
            },
            
            "inventory_status": {
                "patterns": [
                    r"(?:inventory|stock).*(?:status|levels)",
                    r"how much.*(?:inventory|stock)",
                    r"products.*(?:available|in stock)"
                ],
                "queries": [
                    "SELECT COUNT(*) as total_products FROM products",
                    "SELECT category, COUNT(*) as product_count FROM products GROUP BY category ORDER BY product_count DESC",
                    "SELECT AVG(price) as avg_price, MIN(price) as min_price, MAX(price) as max_price FROM products"
                ],
                "category": "inventory"
            },
            
            # Order Analytics Patterns
            "order_analytics": {
                "patterns": [
                    r"(?:order|orders).*(?:analytics|statistics|stats)",
                    r"how many.*orders",
                    r"average.*order.*(?:value|size|amount)"
                ],
                "queries": [
                    "SELECT COUNT(*) as total_orders FROM orders",
                    "SELECT AVG(total_amount) as avg_order_value FROM orders WHERE status = 'completed'",
                    "SELECT status, COUNT(*) as order_count FROM orders GROUP BY status"
                ],
                "category": "orders"
            },
            
            # Growth and Trends
            "growth_trends": {
                "patterns": [
                    r"(?:growth|trend|trending).*(?:sales|revenue|orders)",
                    r"(?:monthly|weekly|daily).*(?:growth|trend)",
                    r"business.*(?:growth|performance|trends)"
                ],
                "queries": [
                    "SELECT DATE(created_at) as order_date, COUNT(*) as daily_orders FROM orders GROUP BY DATE(created_at) ORDER BY order_date DESC LIMIT 30",
                    "SELECT strftime('%Y-%m', created_at) as month, SUM(total_amount) as monthly_revenue FROM orders WHERE status = 'completed' GROUP BY strftime('%Y-%m', created_at) ORDER BY month DESC LIMIT 12"
                ],
                "category": "trends"
            },
            
            # Customer Behavior
            "customer_behavior": {
                "patterns": [
                    r"customer.*(?:behavior|habits|patterns)",
                    r"repeat.*customers",
                    r"customer.*(?:retention|loyalty)"
                ],
                "queries": [
                    "SELECT c.first_name, c.last_name, COUNT(o.id) as order_frequency FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id HAVING COUNT(o.id) > 1 ORDER BY order_frequency DESC",
                    "SELECT AVG(order_count) as avg_orders_per_customer FROM (SELECT customer_id, COUNT(*) as order_count FROM orders GROUP BY customer_id) as customer_orders"
                ],
                "category": "behavior"
            }
        }
    
    def analyze_business_question(self, question: str) -> BusinessInsight:
        """Analyze a business question and provide insights."""
        question_lower = question.lower()
        
        # Find matching patterns
        matched_patterns = []
        for pattern_name, pattern_info in self.business_patterns.items():
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, question_lower):
                    matched_patterns.append((pattern_name, pattern_info))
                    break
        
        if not matched_patterns:
            return self._handle_generic_question(question)
        
        # Execute queries for matched patterns
        insights = []
        all_metrics = []
        
        for pattern_name, pattern_info in matched_patterns:
            metrics = self._execute_pattern_queries(pattern_name, pattern_info)
            all_metrics.extend(metrics)
            
            # Generate insights based on metrics
            pattern_insights = self._generate_insights_for_pattern(pattern_name, pattern_info, metrics)
            insights.extend(pattern_insights)
        
        # Combine insights into a comprehensive business insight
        return BusinessInsight(
            title=self._generate_insight_title(question, matched_patterns),
            description=self._generate_insight_description(question, all_metrics),
            metrics=all_metrics,
            recommendations=self._generate_recommendations(matched_patterns, all_metrics),
            confidence=self._calculate_confidence(matched_patterns, all_metrics)
        )
    
    def _execute_pattern_queries(self, pattern_name: str, pattern_info: Dict) -> List[BusinessMetric]:
        """Execute queries for a specific pattern and return metrics."""
        metrics = []
        
        for query in pattern_info["queries"]:
            try:
                results = cached_query(query)
                if results:
                    metric = self._convert_query_result_to_metric(
                        query, results, pattern_info["category"]
                    )
                    if metric:
                        metrics.append(metric)
            except Exception as e:
                print(f"Error executing query for {pattern_name}: {e}")
                continue
        
        return metrics
    
    def _convert_query_result_to_metric(self, query: str, results: List[Tuple], category: str) -> Optional[BusinessMetric]:
        """Convert query results to a business metric."""
        if not results:
            return None
        
        # Determine metric type based on query
        if "SUM" in query.upper() and "revenue" in query.lower():
            return BusinessMetric(
                name="Total Revenue",
                value=f"${results[0][0]:,.2f}" if results[0][0] else "$0.00",
                description="Total revenue generated",
                category=category
            )
        elif "COUNT" in query.upper() and "customer" in query.lower():
            return BusinessMetric(
                name="Customer Count",
                value=f"{results[0][0]:,}" if results[0][0] else "0",
                description="Total number of customers",
                category=category
            )
        elif "AVG" in query.upper() and "order" in query.lower():
            return BusinessMetric(
                name="Average Order Value",
                value=f"${results[0][0]:,.2f}" if results[0][0] else "$0.00",
                description="Average value per order",
                category=category
            )
        elif "GROUP BY" in query.upper():
            # Handle grouped results
            return BusinessMetric(
                name="Top Results",
                value=f"{len(results)} items analyzed",
                description=f"Analysis of {len(results)} data points",
                category=category
            )
        else:
            # Generic metric
            return BusinessMetric(
                name="Query Result",
                value=str(results[0][0]) if results[0][0] else "No data",
                description="Query result",
                category=category
            )
    
    def _generate_insights_for_pattern(self, pattern_name: str, pattern_info: Dict, metrics: List[BusinessMetric]) -> List[str]:
        """Generate business insights for a specific pattern."""
        insights = []
        
        if pattern_info["category"] == "revenue":
            for metric in metrics:
                if "revenue" in metric.name.lower():
                    if "$0.00" in metric.value:
                        insights.append("Revenue data shows no completed transactions yet.")
                    else:
                        insights.append(f"Revenue performance: {metric.value}")
        
        elif pattern_info["category"] == "customers":
            for metric in metrics:
                if "customer" in metric.name.lower():
                    insights.append(f"Customer base: {metric.value}")
        
        elif pattern_info["category"] == "products":
            insights.append("Product performance analysis completed.")
        
        elif pattern_info["category"] == "trends":
            insights.append("Business trend analysis shows recent activity patterns.")
        
        return insights
    
    def _generate_insight_title(self, question: str, patterns: List[Tuple]) -> str:
        """Generate a title for the business insight."""
        if any("revenue" in p[1]["category"] for p in patterns):
            return "Revenue Analysis"
        elif any("customer" in p[1]["category"] for p in patterns):
            return "Customer Analytics"
        elif any("product" in p[1]["category"] for p in patterns):
            return "Product Performance"
        elif any("trend" in p[1]["category"] for p in patterns):
            return "Business Trends"
        else:
            return "Business Intelligence Report"
    
    def _generate_insight_description(self, question: str, metrics: List[BusinessMetric]) -> str:
        """Generate a description for the business insight."""
        if not metrics:
            return "No relevant data found for the requested analysis."
        
        descriptions = []
        categories = set(metric.category for metric in metrics)
        
        for category in categories:
            category_metrics = [m for m in metrics if m.category == category]
            if category_metrics:
                descriptions.append(f"Analysis of {len(category_metrics)} {category} metrics")
        
        return f"Business intelligence analysis based on {len(metrics)} key metrics across {len(categories)} categories: {', '.join(descriptions)}"
    
    def _generate_recommendations(self, patterns: List[Tuple], metrics: List[BusinessMetric]) -> List[str]:
        """Generate business recommendations based on metrics."""
        recommendations = []
        
        # Revenue recommendations
        revenue_metrics = [m for m in metrics if m.category == "revenue"]
        if revenue_metrics:
            for metric in revenue_metrics:
                if "$0.00" in metric.value:
                    recommendations.append("Consider implementing marketing strategies to generate initial sales")
                else:
                    recommendations.append("Monitor revenue trends and identify growth opportunities")
        
        # Customer recommendations
        customer_metrics = [m for m in metrics if m.category == "customers"]
        if customer_metrics:
            recommendations.append("Focus on customer retention and acquisition strategies")
        
        # Product recommendations
        product_metrics = [m for m in metrics if m.category == "products"]
        if product_metrics:
            recommendations.append("Analyze product performance to optimize inventory and pricing")
        
        # Generic recommendations
        if not recommendations:
            recommendations.append("Continue monitoring key business metrics for insights")
            recommendations.append("Consider implementing data-driven decision making processes")
        
        return recommendations
    
    def _calculate_confidence(self, patterns: List[Tuple], metrics: List[BusinessMetric]) -> float:
        """Calculate confidence level for the analysis."""
        if not metrics:
            return 0.0
        
        # Base confidence on number of successful metrics
        base_confidence = min(len(metrics) / 5.0, 1.0)  # Max confidence with 5+ metrics
        
        # Adjust based on data quality
        non_zero_metrics = [m for m in metrics if m.value not in ["0", "$0.00", "No data"]]
        if non_zero_metrics:
            data_quality = len(non_zero_metrics) / len(metrics)
            return min(base_confidence * data_quality, 1.0)
        
        return base_confidence * 0.5  # Lower confidence for zero/empty data
    
    def _handle_generic_question(self, question: str) -> BusinessInsight:
        """Handle generic business questions that don't match specific patterns."""
        # Try to extract key business terms and provide general insights
        business_terms = {
            "performance": "Business Performance Overview",
            "analysis": "Business Analysis",
            "report": "Business Report",
            "summary": "Business Summary",
            "overview": "Business Overview"
        }
        
        title = "Business Intelligence Inquiry"
        for term, title_option in business_terms.items():
            if term in question.lower():
                title = title_option
                break
        
        # Provide general business metrics
        general_metrics = self._get_general_business_metrics()
        
        return BusinessInsight(
            title=title,
            description="General business intelligence analysis based on available data",
            metrics=general_metrics,
            recommendations=[
                "Review key performance indicators regularly",
                "Consider more specific business questions for detailed analysis",
                "Implement data-driven decision making processes"
            ],
            confidence=0.7
        )
    
    def _get_general_business_metrics(self) -> List[BusinessMetric]:
        """Get general business metrics for overview."""
        metrics = []
        
        try:
            # Basic counts
            queries = [
                ("SELECT COUNT(*) FROM customers", "Total Customers", "customers"),
                ("SELECT COUNT(*) FROM products", "Total Products", "products"),
                ("SELECT COUNT(*) FROM orders", "Total Orders", "orders"),
                ("SELECT COUNT(*) FROM orders WHERE status = 'completed'", "Completed Orders", "orders")
            ]
            
            for query, name, category in queries:
                try:
                    result = cached_query(query)
                    if result:
                        metrics.append(BusinessMetric(
                            name=name,
                            value=f"{result[0][0]:,}",
                            description=f"Total count of {name.lower()}",
                            category=category
                        ))
                except Exception:
                    continue
            
        except Exception as e:
            print(f"Error getting general metrics: {e}")
        
        return metrics
    
    def get_business_summary(self) -> Dict[str, Any]:
        """Get a comprehensive business summary."""
        summary = {
            "overview": {},
            "key_metrics": [],
            "insights": [],
            "recommendations": []
        }
        
        try:
            # Get key business metrics
            key_queries = [
                ("SELECT COUNT(*) FROM customers", "Total Customers"),
                ("SELECT COUNT(*) FROM products", "Total Products"),
                ("SELECT COUNT(*) FROM orders", "Total Orders"),
                ("SELECT SUM(total_amount) FROM orders WHERE status = 'completed'", "Total Revenue"),
                ("SELECT AVG(total_amount) FROM orders WHERE status = 'completed'", "Average Order Value")
            ]
            
            for query, metric_name in key_queries:
                try:
                    result = cached_query(query)
                    if result and result[0][0] is not None:
                        value = result[0][0]
                        if "Revenue" in metric_name or "Order Value" in metric_name:
                            summary["key_metrics"].append(f"{metric_name}: ${value:,.2f}")
                        else:
                            summary["key_metrics"].append(f"{metric_name}: {value:,}")
                except Exception:
                    continue
            
            # Generate insights
            summary["insights"] = [
                "Business data is available for analysis",
                "Multiple data categories are populated",
                "Ready for advanced business intelligence queries"
            ]
            
            # Generate recommendations
            summary["recommendations"] = [
                "Ask specific business questions for detailed analysis",
                "Monitor key performance indicators regularly",
                "Use data-driven insights for strategic decisions"
            ]
            
        except Exception as e:
            summary["error"] = str(e)
        
        return summary


# Global business intelligence engine
_bi_engine = None


def get_business_intelligence() -> BusinessIntelligenceEngine:
    """Get global business intelligence engine."""
    global _bi_engine
    if _bi_engine is None:
        _bi_engine = BusinessIntelligenceEngine()
    return _bi_engine


def analyze_business_question(question: str) -> BusinessInsight:
    """Analyze a business question and return insights."""
    return get_business_intelligence().analyze_business_question(question)


def get_business_summary() -> Dict[str, Any]:
    """Get comprehensive business summary."""
    return get_business_intelligence().get_business_summary()
