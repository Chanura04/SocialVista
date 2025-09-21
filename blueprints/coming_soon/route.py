from flask import request, Blueprint, render_template

from blueprints import coming_soon

coming_soon_bp=Blueprint('coming_soon',__name__,template_folder='templates',static_folder='static')


@coming_soon_bp.route('/')
def coming_soon():
    return render_template('coming_soon.html')


