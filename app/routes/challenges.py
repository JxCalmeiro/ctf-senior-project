import hashlib
from flask import Blueprint, request, jsonify, session
from app.models import db, Challenge, Solve
from flask import send_from_directory
import os

challenges_bp = Blueprint('challenges', __name__)

@challenges_bp.route('/static/challenges/hidden-in-plain-sight')
def hidden_in_plain_sight():
    directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'challenges', 'hidden-in-plain-sight')
    return send_from_directory(directory, 'index.html')

@challenges_bp.route('/static/challenges/recycle-bin-recovery/download')
def recycle_bin_download():
    directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'challenges', 'recycle-bin-recovery')
    return send_from_directory(directory, 'recycle-bin-artifact.zip', as_attachment=True)

@challenges_bp.route('/challenges', methods=['GET'])
def list_challenges():
    if 'user_id' not in session:
        return jsonify({'error': 'not logged in'}), 401

    challenges = Challenge.query.all()
    solved_ids = {s.challenge_id for s in Solve.query.filter_by(user_id=session['user_id']).all()}

    result = []
    for c in challenges:
        result.append({
            'id': c.id,
            'title': c.title,
            'category': c.category,
            'difficulty': c.difficulty,
            'points': c.points,
            'solved': c.id in solved_ids
        })
    return jsonify(result), 200

@challenges_bp.route('/challenges/<int:challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    if 'user_id' not in session:
        return jsonify({'error': 'not logged in'}), 401

    c = Challenge.query.get(challenge_id)
    if not c:
        return jsonify({'error': 'challenge not found'}), 404

    return jsonify({
        'id': c.id,
        'title': c.title,
        'category': c.category,
        'difficulty': c.difficulty,
        'description': c.description,
        'points': c.points
    }), 200

@challenges_bp.route('/challenges/<int:challenge_id>/submit', methods=['POST'])
def submit_flag(challenge_id):
    if 'user_id' not in session:
        return jsonify({'error': 'not logged in'}), 401

    data = request.get_json()
    submitted_flag = data.get('flag', '').strip()

    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        return jsonify({'error': 'challenge not found'}), 404

    already_solved = Solve.query.filter_by(
        user_id=session['user_id'],
        challenge_id=challenge_id
    ).first()
    if already_solved:
        return jsonify({'message': 'already solved'}), 200

    submitted_hash = hashlib.sha256(submitted_flag.encode()).hexdigest()

    if submitted_hash == challenge.flag_hash:
        solve = Solve(
            user_id=session['user_id'],
            challenge_id=challenge_id,
            points_awarded=challenge.points
        )
        db.session.add(solve)
        db.session.commit()
        return jsonify({'correct': True, 'points_awarded': challenge.points}), 200
    else:
        return jsonify({'correct': False}), 200

@challenges_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    from app.models import User
    from sqlalchemy import func

    results = db.session.query(
        User.username,
        func.sum(Solve.points_awarded).label('total_points'),
        func.count(Solve.id).label('solves')
    ).join(Solve, User.id == Solve.user_id) \
     .group_by(User.id) \
     .order_by(func.sum(Solve.points_awarded).desc()) \
     .all()

    return jsonify([
        {'username': r.username, 'points': int(r.total_points), 'solves': r.solves}
        for r in results
    ]), 200
