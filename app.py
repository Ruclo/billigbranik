from tasks.fetch_listings import update_listings
from asyncio import run
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
app = Flask(__name__)

listings_dict = update_listings()

scheduler = BackgroundScheduler()
scheduler.add_job(update_listings, 'cron', hour=0, minute=1)
scheduler.start()
print('scheduler started')

@app.route('/listings', methods=['GET'])
def listings():
    return listings_dict