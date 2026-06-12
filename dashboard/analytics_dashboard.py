# analytics_dashboard.py

import os
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Set theme template to plotly_dark for premium styling
pio.templates.default = "plotly_dark"


def generate_dashboard_html() -> str:
    """
    Reads CSV log files, processes e-commerce recommendation analytics,
    generates Plotly charts, and returns a fully styled responsive HTML page.
    """
    base_dir = Path(__file__).resolve().parent.parent
    analytics_dir = base_dir / "analytics"

    search_log_path = analytics_dir / "search_logs.csv"
    recs_log_path = analytics_dir / "recommendation_logs.csv"
    behavior_log_path = analytics_dir / "user_behavior.csv"

    # Default fallbacks if files are empty
    df_search = pd.read_csv(search_log_path) if search_log_path.exists() else pd.DataFrame(columns=["timestamp", "query", "category", "budget", "results_count", "search_time"])
    df_recs = pd.read_csv(recs_log_path) if recs_log_path.exists() else pd.DataFrame(columns=["timestamp", "product_name", "category", "price", "ratings", "similarity_score"])
    df_behavior = pd.read_csv(behavior_log_path) if behavior_log_path.exists() else pd.DataFrame(columns=["timestamp", "user_id", "action", "product_name", "category"])

    # Compute key stats
    avg_budget = "N/A"
    if not df_search.empty and "budget" in df_search.columns:
        valid_budgets = df_search["budget"].dropna()
        if not valid_budgets.empty:
            avg_budget = f"Rs. {valid_budgets.mean():,.2f}"

    total_searches = len(df_search)
    total_recs = len(df_recs)
    conversion_rate = "0.0%"
    if not df_behavior.empty and total_searches > 0:
        purchases = len(df_behavior[df_behavior["action"] == "purchase"])
        conversion_rate = f"{(purchases / total_searches) * 100:.1f}%"

    # 1. Top Searches Chart (Bar)
    fig_searches = go.Figure()
    if not df_search.empty:
        top_searches = df_search["query"].value_counts().head(8).reset_index()
        top_searches.columns = ["query", "count"]
        fig_searches = px.bar(
            top_searches, 
            x="query", 
            y="count",
            title="Top Search Queries",
            labels={"query": "Search Term", "count": "Search Count"},
            color="count",
            color_continuous_scale="Purples"
        )
        fig_searches.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

    # 2. Popular Categories Chart (Donut Pie)
    fig_categories = go.Figure()
    if not df_search.empty:
        cats = df_search["category"].dropna().value_counts().head(5).reset_index()
        cats.columns = ["category", "count"]
        fig_categories = px.pie(
            cats,
            names="category",
            values="count",
            title="Popular Product Categories",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_categories.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

    # 3. Most Recommended Products (Horizontal Bar)
    fig_recs = go.Figure()
    if not df_recs.empty:
        top_recs = df_recs["product_name"].value_counts().head(5).reset_index()
        top_recs.columns = ["product_name", "count"]
        # Shorten product names for cleaner rendering
        top_recs["display_name"] = top_recs["product_name"].apply(lambda x: x[:30] + "..." if len(str(x)) > 30 else x)
        fig_recs = px.bar(
            top_recs,
            y="display_name",
            x="count",
            orientation="h",
            title="Most Recommended Products",
            labels={"display_name": "Product", "count": "Times Recommended"},
            color="count",
            color_continuous_scale="Blues"
        )
        fig_recs.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

    # 4. Search and Recommendation Trends (Line)
    fig_trends = go.Figure()
    if not df_search.empty:
        # Convert timestamp to date
        df_search["date"] = pd.to_datetime(df_search["timestamp"]).dt.date
        search_counts = df_search.groupby("date").size().reset_index(name="searches")
        
        if not df_recs.empty:
            df_recs["date"] = pd.to_datetime(df_recs["timestamp"]).dt.date
            recs_counts = df_recs.groupby("date").size().reset_index(name="recommendations")
            trends = pd.merge(search_counts, recs_counts, on="date", how="outer").fillna(0)
        else:
            trends = search_counts
            trends["recommendations"] = 0

        fig_trends = go.Figure()
        fig_trends.add_trace(go.Scatter(x=trends["date"], y=trends["searches"], name="Searches", line=dict(color="#bf5af2", width=3)))
        if "recommendations" in trends.columns:
            fig_trends.add_trace(go.Scatter(x=trends["date"], y=trends["recommendations"], name="Recommendations", line=dict(color="#0a84ff", width=3)))
        
        fig_trends.update_layout(
            title="Search vs Recommendation Volume Trends",
            xaxis_title="Date",
            yaxis_title="Volume",
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

    # Convert charts to HTML divs
    div_searches = pio.to_html(fig_searches, full_html=False, include_plotlyjs='cdn')
    div_categories = pio.to_html(fig_categories, full_html=False, include_plotlyjs=False)
    div_recs = pio.to_html(fig_recs, full_html=False, include_plotlyjs=False)
    div_trends = pio.to_html(fig_trends, full_html=False, include_plotlyjs=False)

    # Premium Dashboard HTML Template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aura Commerce AI Discovery Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: rgba(22, 28, 45, 0.45);
            --border-color: rgba(255, 255, 255, 0.08);
            --primary: #bf5af2;
            --secondary: #0a84ff;
            --text-main: #f5f5f7;
            --text-dim: #8e8e93;
            --glass-glow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2.5rem;
            background-image: radial-gradient(circle at 10% 20%, rgba(191, 90, 242, 0.08) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(10, 132, 255, 0.08) 0%, transparent 40%);
        }}

        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
        }}

        h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #fff 30%, var(--primary) 70%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .subtitle {{
            color: var(--text-dim);
            font-size: 1rem;
            margin-top: 0.3rem;
        }}

        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }}

        .kpi-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(12px);
            box-shadow: var(--glass-glow);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-4px);
            border-color: rgba(191, 90, 242, 0.3);
        }}

        .kpi-label {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: var(--text-dim);
            margin-bottom: 0.5rem;
        }}

        .kpi-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 2rem;
            font-weight: 600;
            color: #fff;
        }}

        /* Charts Grid */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 2rem;
        }}

        @media (max-width: 1024px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            body {{
                padding: 1rem;
            }}
        }}

        .chart-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 1.5rem;
            backdrop-filter: blur(12px);
            box-shadow: var(--glass-glow);
            min-height: 400px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .chart-card.full-width {{
            grid-column: span 2;
        }}

        @media (max-width: 1024px) {{
            .chart-card.full-width {{
                grid-column: span 1;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div>
            <h1>Aura Commerce AI</h1>
            <div class="subtitle">Product Recommendation & Discovery Platform Insights</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.9rem; color: var(--text-dim)">Status: Live Monitor</div>
            <div style="font-size: 1.1rem; font-weight: 600; color: var(--secondary)">99.9% API Uptime</div>
        </div>
    </header>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total Discover Queries</div>
            <div class="kpi-value">{total_searches}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Average User Budget</div>
            <div class="kpi-value">{avg_budget}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Recommendations Served</div>
            <div class="kpi-value">{total_recs}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Chatbot Conversion Rate</div>
            <div class="kpi-value">{conversion_rate}</div>
        </div>
    </div>

    <div class="dashboard-grid">
        <div class="chart-card">
            {div_searches}
        </div>
        <div class="chart-card">
            {div_categories}
        </div>
        <div class="chart-card">
            {div_recs}
        </div>
        <div class="chart-card">
            {div_trends}
        </div>
    </div>
</body>
</html>
"""
    return html_content


if __name__ == "__main__":
    # Save dashboard locally for testing
    base_dir = Path(__file__).resolve().parent.parent
    dashboard_file = base_dir / "analytics" / "dashboard.html"
    dashboard_file.parent.mkdir(parents=True, exist_ok=True)
    
    html = generate_dashboard_html()
    with open(dashboard_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard HTML compiled and saved successfully to: {dashboard_file}")
