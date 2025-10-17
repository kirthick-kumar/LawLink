from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Lawyer, Contact, User, Rating
from controllers import rating_dict
import os
from datetime import date

@login_required
def profile_edit():
    lawyer_id = current_user.get_id()
    lawyer = db.session.execute(db.select(Lawyer).where(Lawyer.user_id == lawyer_id)).scalar()
    if request.method == 'POST':
        pic = request.files['lawyer_pic']
        pic.filename = str(lawyer_id)+".png"
        pic_url = os.path.join('static/lawyer_pics/', pic.filename)
        pic.save(pic_url)

        id_pic = request.files['id_pic']
        id_pic.filename = str(lawyer_id)+".png"
        id_pic_url = os.path.join('static/id_pics/', id_pic.filename)
        id_pic.save(id_pic_url)

        pic_url = os.path.join('lawyer_pics/', pic.filename)
        id_url = os.path.join('id_pics/', id_pic.filename)
        name = request.form['name']
        bio = request.form['bio']
        education = request.form['education']
        bar_council_id = request.form['id']
        expertise = request.form['expertise']
        location = request.form['location']
        experience = request.form['experience']
        ongoing = request.form['ongoing']
        won = request.form['won']
        lost = request.form['lost']
        email = request.form['email']
        phone = request.form['phone']
        fee = request.form['fee']
        contacts = request.form['contact'][:-1]
        contact_list = contacts.split('|')
        if lawyer:
            # Editing profile since lawyer profile already exists
            lawyer.name = name
            lawyer.pic_url = pic_url
            lawyer.id_url = id_url
            lawyer.bio = bio
            lawyer.education = education
            lawyer.bar_council_id = bar_council_id
            lawyer.location = location
            lawyer.expertise = expertise
            lawyer.experience = experience
            lawyer.ongoing = ongoing
            lawyer.won = won
            lawyer.lost = lost
            lawyer.email = email
            lawyer.phone = phone
            lawyer.fee = fee
            contact_infos = db.session.execute(db.select(Contact).where(Contact.lawyer_id == lawyer.id)).scalars()
            for contact_info in contact_infos:
                db.session.delete(contact_info)
            for contact in contact_list:
                n = contact.index(':') + 1
                # Characters before : are social media names .ie., from 0 to n
                # Characters after : are usernames .ie., from n to end
                new_contact = Contact(
                    socials=contact[:n],
                    usernames=contact[n:],
                    lawyer=lawyer
                )
                db.session.add(new_contact)
        else:
            # Create profile and save to lawyer database
            try:
                lawyer = Lawyer(name=name,
                                pic_url=pic_url,
                                id_url=id_url,
                                bio=bio,
                                education=education,
                                bar_council_id=bar_council_id,
                                location=location,
                                expertise=expertise,
                                experience=experience,
                                ongoing=ongoing,
                                won=won,
                                lost=lost,
                                phone=phone,
                                email=email,
                                fee=fee,
                                user=current_user)
                db.session.add(lawyer)
                db.session.commit()
            except:
                flash('Bar Council ID already registered to LawLink', 'error')
                return redirect(url_for('profile_edit'))
            # Adding Contact information to Contact Database
            for contact in contact_list:
                n = contact.index(':') + 1
                # Characters before : are social media names .ie., from 0 to n
                # Characters after : are usernames .ie., from n to end
                new_contact = Contact(
                    socials=contact[:n],
                    usernames=contact[n:],
                    lawyer=lawyer
                )
                db.session.add(new_contact)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile', lawyer_id=lawyer.id))
    return render_template('profile_edit.html', lawyer=lawyer)

@login_required
def profile(lawyer_id):
    user = db.session.execute(db.select(User).where(User.id == current_user.get_id())).scalar()
    lawyer = db.get_or_404(Lawyer, lawyer_id)
    if request.method == 'POST':
        if user.id == lawyer.user_id:
            # Approving Reviews
            # Checking if the lawyer profile belongs to the current user
            try:
                ratings = db.session.execute(db.select(Rating).where(Rating.lawyer_id == lawyer_id, Rating.author_id == request.form['approve'])).scalar()
                ratings.verified = True
                lawyer.verified_sum = lawyer.verified_sum + ratings.rating
                lawyer.verified_count = lawyer.verified_count + 1
                flash('Review approved successfully!', 'success')
            except:
                # If the user is not approved remove from list
                ratings = db.session.execute(db.select(Rating).where(Rating.lawyer_id == lawyer_id, Rating.author_id == request.form['delete'])).scalar()
                lawyer.verified_sum = lawyer.verified_sum - ratings.rating
                lawyer.verified_count = lawyer.verified_count - 1
                db.session.delete(ratings)
                flash('Review deleted successfully!', 'success')
            db.session.commit()
        else:
            # Adding/Editing Reviews
            edit_rating = db.session.execute(db.select(Rating).where(Rating.author_id == user.id, Rating.lawyer_id == lawyer_id)).scalar()
            if edit_rating:
                # If edit_rating exists (Old Review), update the rating values and make the verified status as False
                edit_rating.rating = int(request.form['rating_value'])
                edit_rating.review = request.form['review']
                edit_rating.title = request.form['title']
                edit_rating.rating_date = date.today().strftime("on %d %B %Y")
                edit_rating.verified = False
                db.session.commit()
                flash('Review updated successfully!', 'success')
            else:
                # If edit_rating doesn't exist (No Reviews by this user for this lawyer), add a new rating
                new_rating = Rating(
                    rating=request.form['rating_value'],
                    review=request.form['review'],
                    title=request.form['title'],
                    rating_author=user,
                    lawyer=lawyer,
                    rating_date=date.today().strftime("on %d %B %Y")
                )
                db.session.add(new_rating)
                db.session.commit()
                flash('Review submitted successfully!', 'success')
        return redirect(url_for('profile', lawyer_id=lawyer_id))
    # Sending lawyer, user, rating data to profile page
    return render_template('profile.html', lawyer=lawyer, user=user, rating_dict=rating_dict)