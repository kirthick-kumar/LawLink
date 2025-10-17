from flask import render_template, request
from flask_login import login_required, current_user
from models import db, Lawyer
from sqlalchemy import text
from controllers import rating_dict

@login_required
def search():
    # Start with all lawyers
    matching_lawyers = db.session.execute(db.select(Lawyer)).scalars()
    
    if request.method == 'POST':
        # Build query filters based on form data
        filters = []
        
        # Name filter
        if request.form.get('name'):
            name_filter = Lawyer.name.like(f"%{request.form['name']}%")
            filters.append(name_filter)
        
        # Bar Council ID filter
        if request.form.get('bar_council_id'):
            bar_id_filter = text(f"Lawyer.bar_council_id == '{request.form['bar_council_id']}'")
            filters.append(bar_id_filter)
        
        # Expertise filter
        if request.form.get('case'):
            expertise_filter = text(f"Lawyer.expertise == '{request.form['case']}'")
            filters.append(expertise_filter)
        
        # Rating filter
        if request.form.get('rating'):
            rating_value = int(request.form['rating'])
            rating_filter = Lawyer.verified_sum / (Lawyer.verified_count + 0.1) >= rating_value
            filters.append(rating_filter)
        
        # Budget filter
        if request.form.get('budget'):
            budget_filter = text(f"Lawyer.fee <= '{request.form['budget']}'")
            filters.append(budget_filter)
        
        # Experience filter
        if request.form.get('experience'):
            experience_value = int(request.form['experience'])
            experience_filter = text(f"Lawyer.experience >= '{experience_value}'")
            filters.append(experience_filter)
        
        # Win rate filter
        if request.form.get('win'):
            win_rate = int(request.form['win'])
            win_filter = Lawyer.won / (Lawyer.lost + Lawyer.won + 0.1) * 100 >= win_rate
            filters.append(win_filter)
        
        # Location filter
        if request.form.get('location'):
            location_filter = Lawyer.location.like(f"%{request.form['location']}%")
            filters.append(location_filter)
        
        # Apply all filters
        if filters:
            matching_lawyers = db.session.query(Lawyer).filter(*filters)
    
    return render_template('search.html', matching_lawyers=matching_lawyers, rating_dict=rating_dict)