from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat_view'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('Por favor, completa todos los campos requeridos.', 'error')
            return render_template('auth/register.html', name=name, email=email)

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('auth/register.html', name=name, email=email)

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('auth/register.html', name=name, email=email)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Ya existe una cuenta registrada con este correo electrónico.', 'error')
            return render_template('auth/register.html', name=name)

        user = User(
            name=name,
            email=email,
            role='user',
            subscription_tier='free',
            subscription_status='inactive'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'¡Bienvenido a TechHelp IA, {user.name}! Tu cuenta gratuita ha sido creada.', 'success')
        return redirect(url_for('chat.chat_view'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat_view'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Credenciales incorrectas. Verifica tu correo y contraseña.', 'error')
            return render_template('auth/login.html', email=email)

        login_user(user, remember=remember)
        flash(f'Bienvenido de nuevo, {user.name}.', 'success')
        
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('chat.chat_view'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_info':
            name = request.form.get('name', '').strip()
            if name:
                current_user.name = name
                db.session.commit()
                flash('Perfil actualizado con éxito.', 'success')
            else:
                flash('El nombre no puede estar vacío.', 'error')

        elif action == 'change_password':
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')

            if not current_user.check_password(current_pw):
                flash('La contraseña actual es incorrecta.', 'error')
            elif len(new_pw) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres.', 'error')
            elif new_pw != confirm_pw:
                flash('Las nuevas contraseñas no coinciden.', 'error')
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash('Contraseña modificada correctamente.', 'success')

    return render_template('auth/profile.html')
