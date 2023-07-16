from flask import (
    Blueprint, flash, render_template, request, redirect, url_for
)
from werkzeug.exceptions import abort

from flaskAdventure.AdventureGptBE import get_gpt

bp = Blueprint('game', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    gpt = get_gpt()
    if request.method == 'POST':
        return redirect(url_for('game.next'))
    flash('Consulting the Oracle!')
    intro = gpt.game_intro()
    return render_template('game/index.html', intro=intro)


@bp.route('/next', methods= ('GET', 'POST'))
def next():
    gpt = get_gpt()
    flash('The universe evolves ...')
    if request.method == 'POST':
        the_keys = request.form.keys()
        choice = request.form['game_choice']
        result = request.form['the_result']
        result, choices = gpt.generate_a_result(choice, result)
    else:
        result, choices = gpt.generate_a_result("", "")
    return render_template('game/next.html', last_result=result, choices=choices)

