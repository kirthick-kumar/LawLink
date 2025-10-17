from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Lawyer
from controllers import admin_only, rating_dict
from sqlalchemy import text

def delete_profile(lawyer_id):
    """Delete lawyer profile and associated data"""
    from models import Rating, Contact
    
    lawyer = db.session.execute(db.select(Lawyer).where(Lawyer.id == lawyer_id)).scalar()
    if lawyer:
        # Delete associated ratings
        ratings = db.session.execute(db.select(Rating).where(Rating.lawyer_id == lawyer_id)).scalars()
        for rating in ratings:
            db.session.delete(rating)
        
        # Delete associated contacts
        contacts = db.session.execute(db.select(Contact).where(Contact.lawyer_id == lawyer_id)).scalars()
        for contact in contacts:
            db.session.delete(contact)
        
        # Delete lawyer
        db.session.delete(lawyer)

@login_required
@admin_only
def admin():
    matching_lawyers = db.session.execute(db.select(Lawyer)).scalars()
    
    if request.method == 'POST':
        try:
            if 'approve' in request.form:
                # Lawyer Verified
                lawyer = db.session.execute(db.select(Lawyer).where(Lawyer.id == request.form['approve'])).scalar()
                if lawyer:
                    lawyer.verified = True
                    flash(f'Lawyer {lawyer.name} has been verified', 'success')
            elif 'no' in request.form:
                # Lawyer Unverified
                lawyer = db.session.execute(db.select(Lawyer).where(Lawyer.id == request.form['no'])).scalar()
                if lawyer:
                    lawyer.verified = False
                    flash(f'Lawyer {lawyer.name} has been unverified', 'warning')
            elif 'delete' in request.form:
                # Deleting Lawyer
                delete_profile(request.form['delete'])
                flash('Lawyer profile has been deleted', 'success')
        except Exception as e:
            flash(f'Error processing request: {str(e)}', 'error')
        
        db.session.commit()
        matching_lawyers = db.session.execute(db.select(Lawyer)).scalars()
    
    return render_template('admin.html', matching_lawyers=matching_lawyers, rating_dict=rating_dict)

@login_required
def delete_profile_caller():
    """Handle profile deletion from user interface"""
    from models import User, Lawyer
    
    user = db.session.execute(db.select(User).where(User.id == current_user.get_id())).scalar()
    lawyer = db.session.execute(db.select(Lawyer).where(Lawyer.user_id == current_user.get_id())).scalar()
    
    if lawyer and user.id == lawyer.user_id:
        delete_profile(lawyer.id)
        db.session.commit()
        flash('Your profile has been deleted', 'success')
    
    return redirect(url_for('home'))

@admin_only
def chat_debug():
    from controllers.chat_controller import get_chat_stats
    stats = get_chat_stats()
    return {
        'redis_connected': stats['cache_ttl'] != -1,
        'cached_messages': stats['cached_messages'],
        'cache_ttl_seconds': stats['cache_ttl']
    }

@admin_only
def clear_chat_cache_route():
    from controllers.chat_controller import clear_chat_cache
    clear_chat_cache()
    return "Chat cache cleared"