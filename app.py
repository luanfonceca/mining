# -*- coding: utf-8 -*-

from flask.ext import pymongo
from flask import Flask, request, redirect, render_template
from bson.objectid import ObjectId
from json import dumps
from math import log

from random import randint

from config import DATABASE_NAME

app = Flask(__name__)

app.jinja_env.filters['log'] = log
app.config['MONGO_DBNAME'] = DATABASE_NAME
mongo = pymongo.PyMongo(app)


@app.route("/")
def index():
    users = mongo.db.users.find().sort([("_user", pymongo.ASCENDING)])
    return render_template("index.html", users=users, randint=randint)

@app.route("/users_by_skills")
def users_by_skills():
    best_of_all = mongo.db.users.find().sort([
        ("back_end", pymongo.DESCENDING),
        ("front_end", pymongo.DESCENDING),
        ("opened_issues", pymongo.DESCENDING),
        ("setuper", pymongo.DESCENDING),
        ("commiter", pymongo.DESCENDING),
        ("talker", pymongo.DESCENDING),
        ("channeler", pymongo.DESCENDING),
        ("links_shared", pymongo.DESCENDING)
    ])[0]
    back_ender = mongo.db.users.find().sort([("back_end", pymongo.DESCENDING)])[0]
    front_ender = mongo.db.users.find().sort([('back_end', pymongo.DESCENDING)])[0]
    talker = mongo.db.users.find().sort([('talker', pymongo.DESCENDING)])[0]
    channeler = mongo.db.users.find().sort([('channeler', pymongo.DESCENDING)])[0]
    sharer = mongo.db.users.find().sort([('links_shared', pymongo.DESCENDING)])[0]

    return render_template("users_by_skills.html", best_of_all=best_of_all,
        back_ender=back_ender, front_ender=front_ender, talker=talker,
        channeler=channeler, sharer=sharer)

@app.route("/detail/<user>/")
def detail(user):
    user = mongo.db.users.find_one_or_404({'_user': user})
    return render_template("detail.html", user=user, randint=randint)


if __name__ == "__main__":
    app.run(debug=True)
