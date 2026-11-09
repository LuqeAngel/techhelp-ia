from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, User, Conversation, Message
from datetime import date

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acceso restringido: Se requieren permisos de Administrador.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    pro_users = User.query.filter_by(subscription_tier='pro', subscription_status='active').count()
    free_users = total_users - pro_users
    total_conversations = Conversation.query.count()
    total_messages = Message.query.count()

    # Usuarios registrados recientemente
    recent_users = User.query.order_by(User.created_at.desc()).limit(8).all()
    
    # Conversaciones recientes
    recent_conversations = Conversation.query.order_by(Conversation.updated_at.desc()).limit(6).all()

    # Métricas estimadas
    mrr_estimate = pro_users * 19 # 19 USD/EUR al mes

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        pro_users=pro_users,
        free_users=free_users,
        total_conversations=total_conversations,
        total_messages=total_messages,
        recent_users=recent_users,
        recent_conversations=recent_conversations,
        mrr_estimate=mrr_estimate
    )


@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    query = request.args.get('q', '').strip()
    if query:
        users = User.query.filter(
            (User.email.ilike(f'%{query}%')) | (User.name.ilike(f'%{query}%'))
        ).order_by(User.created_at.desc()).all()
    else:
        users = User.query.order_by(User.created_at.desc()).all()

    return render_template('admin/users.html', users=users, query=query)


@admin_bp.route('/user/<int:user_id>/toggle-pro', methods=['POST'])
@login_required
@admin_required
def toggle_user_pro(user_id):
    user = User.query.get_or_404(user_id)
    if user.subscription_tier == 'pro':
        user.subscription_tier = 'free'
        user.subscription_status = 'inactive'
        flash(f'Plan de {user.name} cambiado a Free.', 'info')
    else:
        user.subscription_tier = 'pro'
        user.subscription_status = 'active'
        flash(f'Plan de {user.name} actualizado a PRO con éxito.', 'success')
    
    db.session.commit()
    return redirect(request.referrer or url_for('admin.users_list'))


@admin_bp.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_user_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('No puedes revocar tus propios privilegios de administrador.', 'error')
        return redirect(url_for('admin.users_list'))

    user.role = 'user' if user.role == 'admin' else 'admin'
    db.session.commit()
    flash(f'Rol de {user.name} actualizado a {user.role.upper()}.', 'success')
    return redirect(request.referrer or url_for('admin.users_list'))


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta de administrador.', 'error')
        return redirect(url_for('admin.users_list'))

    name = user.name
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario {name} eliminado permanentemente.', 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/conversations')
@login_required
@admin_required
def conversations_list():
    conversations = Conversation.query.order_by(Conversation.updated_at.desc()).limit(50).all()
    return render_template('admin/conversations.html', conversations=conversations)


@admin_bp.route('/conversation/<int:conv_id>')
@login_required
@admin_required
def conversation_detail(conv_id):
    conv = Conversation.query.get_or_404(conv_id)
    return render_template('admin/conversation_detail.html', conversation=conv)
