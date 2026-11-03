# IMPORTS
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config
from db import execute_query, execute_write
from services import (
    get_influencer_dataframe, calculate_brand_fit_score,
    get_campaign_performance_summary, get_dashboard_stats, get_collaboration_stats,
    get_campaign_budget_chart, get_category_distribution_chart,
    get_engagement_by_category_chart, get_top_influencers_chart,
    get_registration_trend_chart, get_platform_performance_chart,
    get_collaboration_status_chart, get_influencer_availability
)
import os
import uuid
import random

# APP CONFIGURATION.
app = Flask(__name__)
app.config.from_object(Config)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'uploads'), filename)

# HELPER FUNCTIONS
# Check if the logged-in user is an admin
def is_admin():
    return session.get('role') == 'admin'

# Check if a user is currently logged in
def login_required():
    return 'user_id' in session

@app.route('/')
def index():
    # Shows the public home page instead of redirecting immediately
    return render_template('home.html')

@app.route('/products')
def customer_products():
    # Public route (no login required) to show products to customers
    page = request.args.get('page', 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page
    
    # Fetch only 6 products for the current page
    products = execute_query("SELECT * FROM PRODUCT LIMIT %s OFFSET %s", (per_page, offset), fetch_all=True)
    
    # Get the total count of products to calculate total pages
    total_products = execute_query("SELECT COUNT(*) as count FROM PRODUCT", fetch_one=True)['count']
    total_pages = (total_products + per_page - 1) // per_page
    
    return render_template('customer_products.html', 
                           products=products, 
                           page=page, 
                           total_pages=total_pages)

# Add this route anywhere in app.py
@app.route('/api/simulate_live_data')
def simulate_live_data():
    # Fetch all social media posts currently in the database
    items = execute_query("SELECT item_id, reach, likes_count, shares_count, comments_count FROM SOCIAL_MEDIA_ITEM", fetch_all=True)
    
    if items:
        for item in items:
            # Simulate new interactions arriving from social media
            new_likes = item['likes_count'] + random.randint(10, 150)
            new_shares = item['shares_count'] + random.randint(1, 20)
            new_comments = item['comments_count'] + random.randint(1, 10)
            new_reach = item['reach'] + random.randint(50, 300)
            
            # Recalculate the live engagement rate
            rate = ((new_likes + new_shares + new_comments) / new_reach * 100) if new_reach > 0 else 0
            
            # Update the database with the new live data
            execute_write("""
                UPDATE SOCIAL_MEDIA_ITEM 
                SET reach=%s, likes_count=%s, shares_count=%s, comments_count=%s, engagement_rate=%s
                WHERE item_id=%s
            """, (new_reach, new_likes, new_shares, new_comments, round(rate, 2), item['item_id']))
            
    return jsonify({"status": "success", "message": "Live data updated!"})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Fetch user from database by email
        user = execute_query("SELECT * FROM ADMIN WHERE email = %s", (email,), fetch_one=True)

        # Verify password hash
        if user and check_password_hash(user['password'], password):
            # Check if account is deactivated
            if user.get('status') == 'Inactive':
                flash('Your account is deactivated. Contact admin.', 'danger')
                return render_template('login.html')
            
            # Set session variables
            session['user_id'] = user['admin_id']
            session['user_name'] = user['name']
            session['role'] = user.get('role', 'admin')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear all session data to log the user out
    session.clear()
    return redirect(url_for('login'))


# DASHBOARD ROUTES
@app.route('/dashboard')
def dashboard():
    if not login_required(): return redirect(url_for('login'))
    # Fetch aggregated stats for KPI cards and collaboration summaries
    stats = get_dashboard_stats()
    collab = get_collaboration_stats()
    return render_template('dashboard.html', stats=stats, collab=collab)

# These endpoints return JSON data that Chart.js uses to render the graphs
@app.route('/api/chart/campaign_budget')
def api_campaign_budget(): return jsonify(get_campaign_budget_chart())

@app.route('/api/chart/category_distribution')
def api_category_distribution(): return jsonify(get_category_distribution_chart())

@app.route('/api/chart/engagement_by_category')
def api_engagement_by_category(): return jsonify(get_engagement_by_category_chart())

@app.route('/api/chart/top_influencers')
def api_top_influencers(): return jsonify(get_top_influencers_chart())

@app.route('/api/chart/registration_trend')
def api_registration_trend(): return jsonify(get_registration_trend_chart())

@app.route('/api/chart/platform_performance')
def api_platform_performance(): return jsonify(get_platform_performance_chart())

@app.route('/api/chart/collaboration_status')
def api_collaboration_status(): return jsonify(get_collaboration_status_chart())


# INFLUENCER ROUTES
@app.route('/influencers')
def influencers():
    if not login_required(): return redirect(url_for('login'))
    search = request.args.get('search', '')
    category = request.args.get('category', 'All')

    df = get_influencer_dataframe()
    
    # NEW: Pass category to the algorithm to adjust the Brand Fit Score
    influencers_data = calculate_brand_fit_score(df, target_category=category)
    
    # Check availability (prevent double booking)
    busy_influencers = get_influencer_availability()

    for inf in influencers_data:
        if inf['influencer_id'] in busy_influencers:
            inf['is_busy'] = True
            inf['current_campaign'] = busy_influencers[inf['influencer_id']]
        else:
            inf['is_busy'] = False
            inf['current_campaign'] = None

    if search:
        influencers_data = [i for i in influencers_data if search.lower() in i['name'].lower()]

    # NEW: Sort so that Available influencers appear first, then sort by Brand Fit Score
    influencers_data.sort(key=lambda x: (x['is_busy'], -x['brand_fit_score']))

    categories = execute_query("SELECT * FROM CATEGORY", fetch_all=True)
    return render_template('influencers.html', influencers=influencers_data, categories=categories)


@app.route('/influencer/<int:id>')
def influencer_profile(id):
    if not login_required(): return redirect(url_for('login'))
    # Fetch specific influencer details with their aggregated categories
    influencer = execute_query("""
        SELECT i.*, GROUP_CONCAT(c.category_name) as categories 
        FROM INFLUENCER i
        LEFT JOIN INFLUENCER_CATEGORY ic ON i.influencer_id = ic.influencer_id
        LEFT JOIN CATEGORY c ON ic.category_id = c.category_id
        WHERE i.influencer_id = %s GROUP BY i.influencer_id
    """, (id,), fetch_one=True)
    # Fetch contact history
    contacts = execute_query("SELECT * FROM CONTACT WHERE influencer_id = %s", (id,), fetch_all=True)
    return render_template('influencer_profile.html', influencer=influencer, contacts=contacts)


@app.route('/influencer/create', methods=['POST'])
def create_influencer():
    if not login_required(): return redirect(url_for('login'))
    name = request.form['name']
    bio = request.form.get('bio', '')
    followers = int(request.form.get('follower_count', 0))
    engagement = float(request.form.get('engagement_rate', 0))
    status = request.form.get('registration_status', 'Active')
    cats = request.form.getlist('categories')
    
    # Get the URL directly, fallback to UI avatar if empty
    image_url = request.form.get('image_url', '').strip()
    if not image_url:
        image_url = f"https://ui-avatars.com/api/?background=dc2626&color=fff&size=150&name={name}"

    # Insert influencer into database
    inf_id = execute_write("""
        INSERT INTO INFLUENCER (name, bio, follower_count, engagement_rate, 
            registration_status, policy_agreed, policy_agreed_date, image_url)
        VALUES (%s, %s, %s, %s, %s, TRUE, CURDATE(), %s)
    """, (name, bio, followers, engagement, status, image_url))

    # Link categories
    for cid in cats:
        execute_write("INSERT INTO INFLUENCER_CATEGORY (influencer_id, category_id) VALUES (%s,%s)", (inf_id, cid))

    # Add initial contact info if provided
    ctype = request.form.get('contact_type')
    cvalue = request.form.get('contact_value')
    if ctype and cvalue:
        execute_write("""
            INSERT INTO CONTACT (influencer_id, contact_type, contact_value, last_contacted_date, status)
            VALUES (%s,%s,%s,CURDATE(),'New')
        """, (inf_id, ctype, cvalue))

    flash(f'Influencer "{name}" added!', 'success')
    return redirect(url_for('influencers'))


@app.route('/influencer/<int:id>/update', methods=['POST'])
def update_influencer(id):
    if not login_required(): return redirect(url_for('login'))
    name = request.form['name']
    bio = request.form.get('bio', '')
    followers = int(request.form.get('follower_count', 0))
    engagement = float(request.form.get('engagement_rate', 0))
    status = request.form.get('registration_status', 'Active')
    cats = request.form.getlist('categories')
    
    image_url = request.form.get('image_url', '').strip()
    if not image_url:
        image_url = f"https://ui-avatars.com/api/?background=dc2626&color=fff&size=150&name={name}"

    # Update main influencer record
    execute_write("""
        UPDATE INFLUENCER SET name=%s, bio=%s, follower_count=%s, 
            engagement_rate=%s, registration_status=%s, image_url=%s WHERE influencer_id=%s
    """, (name, bio, followers, engagement, status, image_url, id))

    # Clear and re-add categories
    execute_write("DELETE FROM INFLUENCER_CATEGORY WHERE influencer_id=%s", (id,))
    for cid in cats:
        execute_write("INSERT INTO INFLUENCER_CATEGORY (influencer_id, category_id) VALUES (%s,%s)", (id, cid))

    flash('Influencer updated!', 'success')
    return redirect(url_for('influencers'))


@app.route('/influencer/<int:id>/delete', methods=['POST'])
def delete_influencer(id):
    if not login_required(): return redirect(url_for('login'))
    if not is_admin():
        flash('Only admins can delete influencers.', 'danger')
        return redirect(url_for('influencers'))
    # Deletion cascades to categories and contacts due to database foreign keys
    execute_write("DELETE FROM INFLUENCER WHERE influencer_id=%s", (id,))
    flash('Influencer deleted.', 'success')
    return redirect(url_for('influencers'))


@app.route('/category/create', methods=['POST'])
def create_category():
    if not login_required(): return redirect(url_for('login'))
    name = request.form['category_name'].strip()
    if not name:
        flash('Category name required.', 'danger')
        return redirect(request.referrer or url_for('influencers'))
    # Check if category exists
    if execute_query("SELECT * FROM CATEGORY WHERE category_name=%s", (name,), fetch_one=True):
        flash(f'Category "{name}" already exists.', 'warning')
    else:
        execute_write("INSERT INTO CATEGORY (category_name) VALUES (%s)", (name,))
        flash(f'Category "{name}" added!', 'success')
    return redirect(request.referrer or url_for('influencers'))


# CAMPAIGN ROUTES
@app.route('/campaigns')
def campaigns():
    if not login_required(): return redirect(url_for('login'))
    
    data = execute_query("""
        SELECT c.*, p.product_name, p.image_url as product_image_url, a.name as created_by_name,
            (SELECT COUNT(*) FROM CAMPAIGN_INFLUENCER ci WHERE ci.campaign_id = c.campaign_id) as influencer_count,
            (SELECT COALESCE(SUM(ci.agreed_rate), 0) FROM CAMPAIGN_INFLUENCER ci WHERE ci.campaign_id = c.campaign_id) as committed_budget,
            (SELECT COUNT(*) FROM CAMPAIGN_INFLUENCER ci WHERE ci.campaign_id = c.campaign_id AND ci.status = 'Completed') as completed_count
        FROM CAMPAIGN c
        LEFT JOIN PRODUCT p ON c.product_id = p.product_id
        LEFT JOIN ADMIN a ON c.created_by = a.admin_id
        ORDER BY c.campaign_id DESC
    """, fetch_all=True)
    
    products = execute_query("SELECT product_id, product_name FROM PRODUCT", fetch_all=True)
    
    return render_template('campaigns.html', campaigns=data, products=products)


@app.route('/campaign/create', methods=['POST'])
def create_campaign():
    if not login_required(): return redirect(url_for('login'))
    
    product_id = request.form.get('product_id') or None
    
    execute_write("""
        INSERT INTO CAMPAIGN (campaign_name, product_id, budget, start_date, end_date, objective, status, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, 'Active', %s)
    """, (request.form['name'], product_id, request.form['budget'], request.form['start_date'],
          request.form['end_date'], request.form['objective'], session['user_id']))
          
    flash('Campaign created successfully!', 'success')
    return redirect(url_for('campaigns'))


@app.route('/campaign/<int:id>/performance')
def campaign_performance(id):
    if not login_required(): return redirect(url_for('login'))

    campaign = execute_query("""
        SELECT c.*, p.category as product_category, p.product_name 
        FROM CAMPAIGN c 
        LEFT JOIN PRODUCT p ON c.product_id = p.product_id 
        WHERE c.campaign_id = %s
    """, (id,), fetch_one=True)

    influencers_in_campaign = execute_query("""
        SELECT ci.*, i.name as influencer_name, i.follower_count
        FROM CAMPAIGN_INFLUENCER ci
        JOIN INFLUENCER i ON ci.influencer_id = i.influencer_id
        WHERE ci.campaign_id = %s
        ORDER BY ci.campaign_influencer_id DESC
    """, (id,), fetch_all=True)

    if campaign['product_category']:
        all_influencers = execute_query("""
            SELECT DISTINCT i.influencer_id, i.name, i.follower_count 
            FROM INFLUENCER i
            JOIN INFLUENCER_CATEGORY ic ON i.influencer_id = ic.influencer_id
            JOIN CATEGORY c ON ic.category_id = c.category_id
            WHERE c.category_name = %s 
            AND i.influencer_id NOT IN (
                SELECT influencer_id FROM CAMPAIGN_INFLUENCER WHERE status IN ('In Progress', 'Confirmed')
            )
            ORDER BY i.name ASC
        """, (campaign['product_category'],), fetch_all=True)
    else:
        all_influencers = execute_query("SELECT influencer_id, name, follower_count FROM INFLUENCER WHERE registration_status = 'Active'", fetch_all=True)

    performance_data = execute_query("""
        SELECT sm.*, i.name as influencer_name, ci.target_engagement_rate
        FROM SOCIAL_MEDIA_ITEM sm
        JOIN CAMPAIGN_INFLUENCER ci ON sm.campaign_influencer_id = ci.campaign_influencer_id
        JOIN INFLUENCER i ON ci.influencer_id = i.influencer_id
        WHERE ci.campaign_id = %s
        ORDER BY sm.recorded_date DESC
    """, (id,), fetch_all=True)

    summary = get_campaign_performance_summary(id)

    return render_template('campaign_performance.html',
                           campaign=campaign, influencers=influencers_in_campaign, 
                           all_influencers=all_influencers, performance=performance_data, summary=summary)

@app.route('/api/live_metrics/<int:ci_id>')
def live_metrics(ci_id):
    existing_metric = execute_query("""
        SELECT item_id, reach, likes_count, shares_count, comments_count 
        FROM SOCIAL_MEDIA_ITEM 
        WHERE campaign_influencer_id = %s AND platform_name = 'Live API Sync'
    """, (ci_id,), fetch_one=True)

    if existing_metric:
        new_reach = existing_metric['reach'] + random.randint(100, 500)
        new_likes = existing_metric['likes_count'] + random.randint(10, 50)
        new_shares = existing_metric['shares_count'] + random.randint(1, 10)
        new_comments = existing_metric['comments_count'] + random.randint(1, 5)
        
        rate = ((new_likes + new_shares + new_comments) / new_reach * 100) if new_reach > 0 else 0
        
        execute_write("""
            UPDATE SOCIAL_MEDIA_ITEM 
            SET reach=%s, likes_count=%s, shares_count=%s, comments_count=%s, engagement_rate=%s
            WHERE item_id=%s
        """, (new_reach, new_likes, new_shares, new_comments, round(rate, 2), existing_metric['item_id']))

    else:
        base_reach = random.randint(10000, 50000)
        likes = int(base_reach * random.uniform(0.05, 0.15))
        comments = int(likes * 0.1)
        shares = int(likes * 0.05)
        reach = base_reach + likes
        rate = ((likes + shares + comments) / reach * 100) if reach > 0 else 0
        
        execute_write("""
            INSERT INTO SOCIAL_MEDIA_ITEM 
            (campaign_influencer_id, platform_name, reach, likes_count, shares_count, comments_count, engagement_rate, recorded_date)
            VALUES (%s,'Live API Sync',%s,%s,%s,%s,%s,CURDATE())
        """, (ci_id, reach, likes, shares, comments, round(rate, 2)))
        
    return jsonify({"status": "success"})


@app.route('/add_performance', methods=['POST'])
def add_performance():
    if not login_required(): return redirect(url_for('login'))
    ci_id = request.form['campaign_influencer_id']
    reach = int(request.form['reach'])
    likes = int(request.form['likes'])
    shares = int(request.form['shares'])
    comments = int(request.form['comments'])
    
    # AUTOMATIC CALCULATION OF ENGAGEMENT RATE
    rate = ((likes + shares + comments) / reach * 100) if reach > 0 else 0

    execute_write("""
        INSERT INTO SOCIAL_MEDIA_ITEM 
        (campaign_influencer_id, platform_name, reach, likes_count, shares_count, comments_count, engagement_rate, recorded_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,CURDATE())
    """, (ci_id, request.form['platform'], reach, likes, shares, comments, round(rate, 2)))

    flash('Performance logged!', 'success')
    return redirect(request.referrer)


@app.route('/campaign/<int:campaign_id>/assign', methods=['POST'])
def assign_influencer(campaign_id):
    if not login_required():
        return redirect(url_for('login'))

    influencer_id = request.form['influencer_id']
    agreed_rate = request.form.get('agreed_rate', 0) or 0
    deliverable_date = request.form.get('deliverable_date') or None
    status = request.form.get('status', 'Pending')
    
    # NEW: Get the threshold
    target_engagement = float(request.form.get('target_engagement_rate', 0) or 0)

    existing = execute_query("""
        SELECT * FROM CAMPAIGN_INFLUENCER 
        WHERE campaign_id = %s AND influencer_id = %s
    """, (campaign_id, influencer_id), fetch_one=True)

    if existing:
        flash('This influencer is already assigned to this campaign.', 'warning')
        return redirect(url_for('campaign_performance', id=campaign_id))

    # NEW: Save threshold to database
    execute_write("""
        INSERT INTO CAMPAIGN_INFLUENCER 
        (campaign_id, influencer_id, agreed_rate, deliverable_date, status, target_engagement_rate)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (campaign_id, influencer_id, agreed_rate, deliverable_date, status, target_engagement))

    flash('Influencer assigned to campaign with KPI threshold!', 'success')
    return redirect(url_for('campaign_performance', id=campaign_id))


@app.route('/collaboration/<int:ci_id>/update', methods=['POST'])
def update_collaboration(ci_id):
    if not login_required():
        return redirect(url_for('login'))

    agreed_rate = request.form.get('agreed_rate', 0) or 0
    deliverable_date = request.form.get('deliverable_date') or None
    status = request.form.get('status', 'Pending')
    
    # NEW: Get updated threshold
    target_engagement = float(request.form.get('target_engagement_rate', 0) or 0)

    ci = execute_query(
        "SELECT campaign_id FROM CAMPAIGN_INFLUENCER WHERE campaign_influencer_id = %s",
        (ci_id,), fetch_one=True
    )

    # NEW: Update threshold in database
    execute_write("""
        UPDATE CAMPAIGN_INFLUENCER 
        SET agreed_rate = %s, deliverable_date = %s, status = %s, target_engagement_rate = %s
        WHERE campaign_influencer_id = %s
    """, (agreed_rate, deliverable_date, status, target_engagement, ci_id))

    flash('Collaboration & KPI Threshold updated!', 'success')
    return redirect(url_for('campaign_performance', id=ci['campaign_id']))

@app.route('/collaboration/<int:ci_id>/remove', methods=['POST'])
def remove_collaboration(ci_id):
    if not login_required():
        return redirect(url_for('login'))

    if not is_admin():
        flash('Only admins can remove influencers from campaigns.', 'danger')
        return redirect(url_for('campaigns'))

    ci = execute_query(
        "SELECT campaign_id FROM CAMPAIGN_INFLUENCER WHERE campaign_influencer_id = %s",
        (ci_id,), fetch_one=True
    )

    execute_write("DELETE FROM CAMPAIGN_INFLUENCER WHERE campaign_influencer_id = %s", (ci_id,))
    flash('🗑️ Influencer removed from campaign.', 'success')
    return redirect(url_for('campaign_performance', id=ci['campaign_id']))


# STAFF MANAGEMENT ROUTES (Admin Only)
@app.route('/staff')
def staff_list():
    if not login_required(): return redirect(url_for('login'))
    if not is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard'))
    staff = execute_query("SELECT * FROM ADMIN WHERE role='staff' ORDER BY registered_at DESC", fetch_all=True)
    return render_template('staff.html', staff=staff)


@app.route('/staff/create', methods=['POST'])
def create_staff():
    if not login_required(): return redirect(url_for('login'))
    if not is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard'))

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    if execute_query("SELECT * FROM ADMIN WHERE email=%s", (email,), fetch_one=True):
        flash('Email already registered.', 'danger')
        return redirect(url_for('staff_list'))

    execute_write("""
        INSERT INTO ADMIN (name, email, password, role, status)
        VALUES (%s,%s,%s,'staff','Active')
    """, (name, email, generate_password_hash(password)))

    flash(f'Staff "{name}" added!', 'success')
    return redirect(url_for('staff_list'))


@app.route('/staff/<int:id>/toggle', methods=['POST'])
def toggle_staff_status(id):
    if not login_required(): return redirect(url_for('login'))
    if not is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))

    s = execute_query("SELECT * FROM ADMIN WHERE admin_id=%s", (id,), fetch_one=True)
    # Prevent modifying the main system admin
    if not s or s['role'] == 'admin':
        flash('Cannot modify this account.', 'danger')
        return redirect(url_for('staff_list'))

    new_status = 'Inactive' if s['status'] == 'Active' else 'Active'
    execute_write("UPDATE ADMIN SET status=%s WHERE admin_id=%s", (new_status, id))
    flash(f'✅ Status → {new_status}', 'success')
    return redirect(url_for('staff_list'))


@app.route('/staff/<int:id>/delete', methods=['POST'])
def delete_staff(id):
    if not login_required(): return redirect(url_for('login'))
    if not is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    # Prevent self-deletion
    if id == session['user_id']:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('staff_list'))

    execute_write("DELETE FROM ADMIN WHERE admin_id=%s AND role='staff'", (id,))
    flash('🗑️ Staff deleted.', 'success')
    return redirect(url_for('staff_list'))


# APP INITIALIZATION
def ensure_default_admin():
    admin = execute_query("SELECT * FROM ADMIN WHERE email=%s", ('admin@system.com',), fetch_one=True)
    hashed = generate_password_hash('admin123')
    if not admin:
        execute_write("""
            INSERT INTO ADMIN (name, email, password, role, status)
            VALUES ('System Admin','admin@system.com',%s,'admin','Active')
        """, (hashed,))
        print("Default admin created: admin@system.com / admin123")
    else:
        execute_write("UPDATE ADMIN SET password=%s, role='admin', status='Active' WHERE email=%s", (hashed, 'admin@system.com'))
        print("Admin password refreshed: admin@system.com / admin123")


@app.route('/api/auto_grow_metrics')
def auto_grow_metrics():
    # Fetch all influencers to grow their followers and engagement
    influencers = execute_query("SELECT influencer_id, follower_count, engagement_rate FROM INFLUENCER", fetch_all=True)
    
    if influencers:
        for inf in influencers:
            new_followers = inf['follower_count'] + random.randint(10, 100)
            new_engagement = round(inf['engagement_rate'] + random.uniform(0.1, 0.5), 2)
            execute_write("UPDATE INFLUENCER SET follower_count=%s, engagement_rate=%s WHERE influencer_id=%s", 
                          (new_followers, new_engagement, inf['influencer_id']))

    # Fetch social media items to grow campaign stats
    items = execute_query("SELECT item_id, reach, likes_count, shares_count, comments_count FROM SOCIAL_MEDIA_ITEM", fetch_all=True)
    
    if items:
        for item in items:
            new_likes = item['likes_count'] + random.randint(5, 50)
            new_shares = item['shares_count'] + random.randint(1, 10)
            new_comments = item['comments_count'] + random.randint(1, 5)
            new_reach = item['reach'] + random.randint(20, 100)
            
            rate = ((new_likes + new_shares + new_comments) / new_reach * 100) if new_reach > 0 else 0
            
            execute_write("""
                UPDATE SOCIAL_MEDIA_ITEM 
                SET reach=%s, likes_count=%s, shares_count=%s, comments_count=%s, engagement_rate=%s
                WHERE item_id=%s
            """, (new_reach, new_likes, new_shares, new_comments, round(rate, 2), item['item_id']))
            
    return jsonify({"status": "success"})


if __name__ == '__main__':
    # Create tables/seed data if needed on first run
    with app.app_context():
        try:
            ensure_default_admin()
        except Exception as e:
            print(f"Init error: {e}")
    app.run(debug=True)