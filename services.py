import pandas as pd
from db import execute_query


def get_influencer_dataframe():
    query = """
        SELECT i.influencer_id, i.name, i.follower_count, i.engagement_rate, 
               i.registration_status, i.registered_at,
               GROUP_CONCAT(c.category_name) as categories
        FROM INFLUENCER i
        LEFT JOIN INFLUENCER_CATEGORY ic ON i.influencer_id = ic.influencer_id
        LEFT JOIN CATEGORY c ON ic.category_id = c.category_id
        GROUP BY i.influencer_id
    """
    data = execute_query(query, fetch_all=True)
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)


def calculate_brand_fit_score(df, target_category=None, min_followers=0):
    if df.empty:
        return []
    df['engagement_rate'] = df['engagement_rate'].fillna(0.0)
    df['follower_count'] = df['follower_count'].fillna(0)
    df['categories'] = df['categories'].fillna('Uncategorized')

    if min_followers > 0:
        df = df[df['follower_count'] >= min_followers]
        
    if target_category and target_category != 'All':
        df = df[df['categories'].str.contains(target_category, case=False, na=False)]

    max_followers = df['follower_count'].max() if not df.empty else 1
    df['follower_score'] = df['follower_count'] / max_followers

    max_engagement = df['engagement_rate'].max() if not df.empty else 1
    df['engagement_score'] = df['engagement_rate'] / max_engagement

    # Calculate base score
    df['brand_fit_score'] = (df['follower_score'] * 0.4) + (df['engagement_score'] * 0.6)
    df['brand_fit_score'] = (df['brand_fit_score'] * 100).round(2)

    df = df.sort_values(by='brand_fit_score', ascending=False)
    return df.to_dict(orient='records')


def get_campaign_performance_summary(campaign_id):
    query = """
        SELECT sm.platform_name, sm.reach, sm.likes_count, sm.shares_count, sm.comments_count
        FROM SOCIAL_MEDIA_ITEM sm
        JOIN CAMPAIGN_INFLUENCER ci ON sm.campaign_influencer_id = ci.campaign_influencer_id
        WHERE ci.campaign_id = %s
    """
    data = execute_query(query, (campaign_id,), fetch_all=True)
    if not data:
        return {"total_reach": 0, "total_engagement": 0, "avg_engagement_rate": 0}

    df = pd.DataFrame(data)
    total_reach = int(df['reach'].sum())
    df['total_engagement'] = df['likes_count'] + df['shares_count'] + df['comments_count']
    total_engagement = int(df['total_engagement'].sum())
    avg_rate = (total_engagement / total_reach * 100) if total_reach > 0 else 0

    return {
        "total_reach": total_reach,
        "total_engagement": total_engagement,
        "avg_engagement_rate": round(avg_rate, 2)
    }


def get_dashboard_stats():
    total_influencers = execute_query("SELECT COUNT(*) as t FROM INFLUENCER", fetch_one=True)['t']
    active_campaigns = execute_query("SELECT COUNT(*) as t FROM CAMPAIGN WHERE status='Active'", fetch_one=True)['t']
    total_campaigns = execute_query("SELECT COUNT(*) as t FROM CAMPAIGN", fetch_one=True)['t']
    total_staff = execute_query("SELECT COUNT(*) as t FROM ADMIN WHERE role='staff'", fetch_one=True)['t']

    budget = execute_query("SELECT SUM(budget) as t FROM CAMPAIGN", fetch_one=True)['t'] or 0
    spent = execute_query("SELECT SUM(ci.agreed_rate) as t FROM CAMPAIGN_INFLUENCER ci", fetch_one=True)['t'] or 0

    reach_res = execute_query("SELECT SUM(reach) as t FROM SOCIAL_MEDIA_ITEM", fetch_one=True)
    total_reach = reach_res['t'] if reach_res and reach_res['t'] else 0

    return {
        'total_influencers': total_influencers,
        'active_campaigns': active_campaigns,
        'total_campaigns': total_campaigns,
        'total_staff': total_staff,
        'total_budget': float(budget),
        'spent_budget': float(spent),
        'total_reach': int(total_reach)
    }


def get_collaboration_stats():
    """Overall collaboration KPIs for the dashboard."""
    stats = execute_query("""
        SELECT 
            COUNT(*) as total_assignments,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
            COALESCE(SUM(agreed_rate), 0) as total_committed
        FROM CAMPAIGN_INFLUENCER
    """, fetch_one=True)
    return stats or {'total_assignments': 0, 'completed': 0, 'in_progress': 0, 'pending': 0, 'total_committed': 0}


def get_campaign_budget_chart():
    data = execute_query("SELECT campaign_name, budget FROM CAMPAIGN ORDER BY budget DESC", fetch_all=True)
    if not data:
        return {'labels': [], 'values': []}
    df = pd.DataFrame(data)
    return {'labels': df['campaign_name'].tolist(), 'values': df['budget'].astype(float).tolist()}


def get_category_distribution_chart():
    data = execute_query("""
        SELECT c.category_name, COUNT(ic.influencer_id) as count
        FROM CATEGORY c
        LEFT JOIN INFLUENCER_CATEGORY ic ON c.category_id = ic.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY count DESC
    """, fetch_all=True)
    if not data:
        return {'labels': [], 'values': []}
    df = pd.DataFrame(data)
    return {'labels': df['category_name'].tolist(), 'values': df['count'].astype(int).tolist()}


def get_engagement_by_category_chart():
    data = execute_query("""
        SELECT c.category_name, i.engagement_rate
        FROM INFLUENCER i
        JOIN INFLUENCER_CATEGORY ic ON i.influencer_id = ic.influencer_id
        JOIN CATEGORY c ON ic.category_id = c.category_id
    """, fetch_all=True)
    if not data:
        return {'labels': [], 'values': []}
    df = pd.DataFrame(data)
    grouped = df.groupby('category_name')['engagement_rate'].mean().round(2).sort_values(ascending=False)
    return {'labels': grouped.index.tolist(), 'values': grouped.values.tolist()}


def get_top_influencers_chart(limit=5):
    df = get_influencer_dataframe()
    if df.empty:
        return {'labels': [], 'followers': [], 'engagement': []}
    df['engagement_rate'] = df['engagement_rate'].fillna(0)
    df['follower_count'] = df['follower_count'].fillna(0)
    top = df.nlargest(limit, 'engagement_rate')
    return {
        'labels': top['name'].tolist(),
        'followers': top['follower_count'].astype(int).tolist(),
        'engagement': top['engagement_rate'].astype(float).tolist()
    }


def get_registration_trend_chart():
    data = execute_query("""
        SELECT DATE_FORMAT(registered_at, '%Y-%m') as month, COUNT(*) as count
        FROM INFLUENCER
        GROUP BY DATE_FORMAT(registered_at, '%Y-%m')
        ORDER BY month ASC
        LIMIT 6
    """, fetch_all=True)
    if not data:
        return {'labels': [], 'values': []}
    df = pd.DataFrame(data)
    return {'labels': df['month'].tolist(), 'values': df['count'].astype(int).tolist()}


def get_platform_performance_chart():
    data = execute_query("""
        SELECT platform_name, SUM(reach) as total_reach, 
               SUM(likes_count + shares_count + comments_count) as total_engagement
        FROM SOCIAL_MEDIA_ITEM
        GROUP BY platform_name
    """, fetch_all=True)
    if not data:
        return {'labels': [], 'reach': [], 'engagement': []}
    df = pd.DataFrame(data)
    return {
        'labels': df['platform_name'].tolist(),
        'reach': df['total_reach'].astype(int).tolist(),
        'engagement': df['total_engagement'].astype(int).tolist()
    }


def get_collaboration_status_chart():
    data = execute_query("""
        SELECT status, COUNT(*) as count
        FROM CAMPAIGN_INFLUENCER
        GROUP BY status
    """, fetch_all=True)
    if not data:
        return {'labels': [], 'values': []}
    df = pd.DataFrame(data)
    return {'labels': df['status'].tolist(), 'values': df['count'].astype(int).tolist()}

def get_influencer_availability():
    """Checks which influencers are currently assigned to 'Active' or 'In Progress' campaigns."""
    query = """
        SELECT DISTINCT i.influencer_id, c.campaign_name 
        FROM INFLUENCER i
        JOIN CAMPAIGN_INFLUENCER ci ON i.influencer_id = ci.influencer_id
        JOIN CAMPAIGN c ON ci.campaign_id = c.campaign_id
        WHERE ci.status IN ('In Progress', 'Confirmed') 
        AND c.status = 'Active'
    """
    data = execute_query(query, fetch_all=True)
    # Returns a dictionary: {influencer_id: campaign_name}
    return {row['influencer_id']: row['campaign_name'] for row in data} if data else {}