"""
Analytics and insights engine
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class AnalyticsEngine:
    """Provides advanced analytics and insights"""

    def __init__(self):
        from managers.data_manager import data_manager
        self.app_data = data_manager.get_data()

    def get_spending_trends(self, months: List[str], category: Optional[str] = None) -> Dict[str, Any]:
        """Get spending trends over time"""
        try:
            trends = {
                'data': {},
                'trend_direction': 'stable',
                'average': 0,
                'total': 0,
                'min': 0,
                'max': 0
            }

            spending_data = []

            for month in months:
                transactions = self.app_data.transactions.get(month, [])

                if category:
                    month_spending = sum(t['amount'] for t in transactions 
                                       if t.get('category') == category)
                else:
                    month_spending = sum(t['amount'] for t in transactions)

                trends['data'][month] = month_spending
                spending_data.append(month_spending)

            if spending_data:
                trends['average'] = sum(spending_data) / len(spending_data)
                trends['total'] = sum(spending_data)
                trends['min'] = min(spending_data)
                trends['max'] = max(spending_data)

                # Determine trend direction
                if len(spending_data) >= 3:
                    recent_avg = sum(spending_data[-3:]) / 3
                    older_avg = sum(spending_data[:3]) / 3

                    if recent_avg > older_avg * 1.1:
                        trends['trend_direction'] = 'increasing'
                    elif recent_avg < older_avg * 0.9:
                        trends['trend_direction'] = 'decreasing'

            return trends

        except Exception as e:
            logging.error(f"Error calculating trends: {e}")
            return {'data': {}, 'trend_direction': 'unknown', 'average': 0}

    def get_category_performance(self) -> List[Dict[str, Any]]:
        """Get performance analysis for all categories"""
        try:
            performance = []

            # Get all categories
            all_categories = set()
            for group_categories in self.app_data.categories.values():
                all_categories.update(group_categories)

            for category in all_categories:
                cat_data = self.analyze_category(category)
                performance.append(cat_data)

            # Sort by total spending
            performance.sort(key=lambda x: x['total_spent'], reverse=True)

            return performance

        except Exception as e:
            logging.error(f"Error analyzing category performance: {e}")
            return []

    def analyze_category(self, category: str) -> Dict[str, Any]:
        """Analyze a specific category"""
        analysis = {
            'category': category,
            'total_spent': 0,
            'total_budget': 0,
            'adherence_rate': 0,
            'months_over_budget': 0,
            'months_with_data': 0,
            'average_monthly': 0
        }

        monthly_spending = []

        for month in self.app_data.transactions.keys():
            transactions = self.app_data.transactions[month]
            month_spending = sum(t['amount'] for t in transactions 
                               if t.get('category') == category)

            if month_spending > 0:
                analysis['months_with_data'] += 1
                monthly_spending.append(month_spending)
                analysis['total_spent'] += month_spending

                # Check budget
                month_budget = self.app_data.budgets.get(month, {}).get(category, 0)
                if month_budget > 0:
                    analysis['total_budget'] += month_budget
                    if month_spending > month_budget:
                        analysis['months_over_budget'] += 1

        if analysis['months_with_data'] > 0:
            analysis['average_monthly'] = analysis['total_spent'] / analysis['months_with_data']

        if analysis['total_budget'] > 0:
            analysis['adherence_rate'] = (analysis['total_spent'] / analysis['total_budget']) * 100

        return analysis

    def detect_anomalies(self, category: str = None) -> List[Dict[str, Any]]:
        """Detect spending anomalies"""
        anomalies = []

        # TODO: Implement anomaly detection algorithm
        # This would analyze spending patterns and identify unusual transactions

        return anomalies

    def get_insights(self) -> List[str]:
        """Generate actionable insights"""
        insights = []

        # Analyze overall spending
        total_spending = sum(
            sum(t['amount'] for t in transactions)
            for transactions in self.app_data.transactions.values()
        )

        total_budget = sum(
            sum(budgets.values())
            for budgets in self.app_data.budgets.values()
        )

        if total_budget > 0:
            adherence = (total_spending / total_budget) * 100
            if adherence > 110:
                insights.append("⚠️ Overall spending exceeds budget by more than 10%")
            elif adherence < 90:
                insights.append("✅ Good job! You're under budget by more than 10%")

        # Category-specific insights
        performance = self.get_category_performance()
        for cat_perf in performance[:3]:  # Top 3 spending categories
            if cat_perf['adherence_rate'] > 120:
                insights.append(f"💰 {cat_perf['category']} is significantly over budget")

        return insights
