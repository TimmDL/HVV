# predictive_insights.py
import pandas as pd

def basic_predictive_insights(df):
    insights = []

    def get_top_issues_for_state(state, top_n=5):
        issue_counts = df[df['state'] == state]['LmuId'].value_counts().head(top_n)
        return issue_counts

    top_out_of_order = get_top_issues_for_state('OUT_OF_ORDER')
    insights.append("Top 5 Machines with Most 'OUT_OF_ORDER' Issues:")
    for lmu_id, count in top_out_of_order.items():
        insights.append(f"  {lmu_id}: {count} issues")

    top_warning = get_top_issues_for_state('WARNING')
    insights.append("Top 5 Machines with Most 'WARNING' Issues:")
    for lmu_id, count in top_warning.items():
        insights.append(f"  {lmu_id}: {count} issues")

    return insights
