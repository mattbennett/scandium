from flask import render_template
from {{project_name}} import sc


@sc.app.route("/")
def index():
    return render_template('index.html')