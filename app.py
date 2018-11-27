from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from startup_setup import Startup, Base, Founder

from flask import session as login_session
import random
import string

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///startup.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Show all startups
@app.route('/')
@app.route('/startup/')
def showStartups():
    startups = session.query(Startup).order_by(asc(Startup.name))
    return render_template('startups.html', startups=startups)

@app.route('/startup/<int:startup_id>/')
@app.route('/startup/<int:startup_id>/detail/')
def showDetail(startup_id):
    startup = session.query(Startup).filter_by(id=startup_id).one()
    founders = session.query(Founder).filter_by(
        startup_id=startup_id).all()
    return render_template('detail.html', founders=founders, startup=startup)

# Create a new founder
@app.route('/startup/<int:startup_id>/detail/new/', methods=['GET', 'POST'])
def newFounder(startup_id):
    startup = session.query(Startup).filter_by(id=startup_id).one()
    if request.method == 'POST':
        newfounder = Founder(name=request.form['name'], bio=request.form['bio'], startup_id=startup_id)
        session.add(newfounder)
        session.commit()
        flash('New Founder %s Successfully Created' % (newfounder.name))
        return redirect(url_for('showDetail', startup_id=startup_id))
    else:
        return render_template('newfounder.html', startup_id=startup_id)

# Edit founder
@app.route('/startup/<int:startup_id>/detail/<int:founder_id>/edit', methods=['GET', 'POST'])
def editFounder(startup_id,founder_id):

    editedfounder = session.query(Founder).filter_by(id=founder_id).one()
    startup = session.query(Startup).filter_by(id=startup_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedfounder.name = request.form['name']
        if request.form['bio']:
            editedfounder.bio = request.form['bio']
        session.add(editedfounder)
        session.commit()
        flash('Founder Successfully Edited')
        return redirect(url_for('showDetail', startup_id=startup_id))
    else:
        return render_template('editfounder.html', startup_id=startup_id, founder_id=founder_id, founder=editedfounder)


# Delete founder
@app.route('/startup/<int:startup_id>/detail/<int:founder_id>/delete', methods=['GET', 'POST'])
def deleteFounder(startup_id,founder_id):
    startup = session.query(Startup).filter_by(id=startup_id).one()
    founderToDelete = session.query(Founder).filter_by(id=founder_id).one()
    if request.method == 'POST':
        session.delete(founderToDelete)
        session.commit()
        flash('Founder Successfully Deleted')
        return redirect(url_for('showDetail', startup_id=startup_id))
    else:
        return render_template('deletefounder.html', founder=founderToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
