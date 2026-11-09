from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from config import Config
from models import db, User
from services.stripe_service import (
    create_checkout_session,
    handle_webhook_event,
    create_portal_session,
    is_stripe_configured
)

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/pricing')
def pricing():
    stripe_ready = is_stripe_configured()
    return render_template(
        'billing/pricing.html',
        stripe_ready=stripe_ready,
        free_limit=Config.FREE_TIER_DAILY_LIMIT,
        stripe_publishable_key=Config.STRIPE_PUBLISHABLE_KEY
    )


@billing_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    if current_user.is_pro():
        flash('Ya tienes una suscripción Pro activa.', 'info')
        return redirect(url_for('chat.chat_view'))

    success_url = Config.BASE_URL + url_for('billing.success')
    cancel_url = Config.BASE_URL + url_for('billing.cancel')

    checkout_url = create_checkout_session(current_user, success_url, cancel_url)

    if checkout_url:
        return redirect(checkout_url, code=303)

    # Si Stripe aún no está configurado (modo desarrollo/demo)
    flash(
        'Modo Demo: Claves de Stripe aún no configuradas. Puedes probar el plan Pro activándolo en un clic con el botón de abajo.',
        'warning'
    )
    return redirect(url_for('billing.pricing', dev_mode='1'))


@billing_bp.route('/billing/success')
@login_required
def success():
    # En desarrollo directo o retorno de checkout
    session_id = request.args.get('session_id')
    if session_id or not is_stripe_configured():
        current_user.subscription_tier = 'pro'
        current_user.subscription_status = 'active'
        db.session.commit()

    flash('¡Felicidades! Tu suscripción a TechHelp Pro está activa. Tienes consultas ilimitadas.', 'success')
    return render_template('billing/success.html')


@billing_bp.route('/billing/cancel')
@login_required
def cancel():
    flash('El proceso de suscripción fue cancelado. Tu cuenta sigue en el plan Gratuito.', 'info')
    return render_template('billing/cancel.html')


@billing_bp.route('/billing/portal')
@login_required
def customer_portal():
    return_url = Config.BASE_URL + url_for('billing.pricing')
    portal_url = create_portal_session(current_user, return_url)
    if portal_url:
        return redirect(portal_url)
    
    flash('El portal de Stripe no está disponible en este momento.', 'warning')
    return redirect(url_for('billing.pricing'))


@billing_bp.route('/billing/dev-upgrade', methods=['POST'])
@login_required
def dev_upgrade():
    """Ruta para alternar el plan Pro en entornos de desarrollo sin requerir tarjeta Stripe real."""
    if current_user.is_pro():
        current_user.subscription_tier = 'free'
        current_user.subscription_status = 'inactive'
        flash('Has vuelto al plan Free de prueba.', 'info')
    else:
        current_user.subscription_tier = 'pro'
        current_user.subscription_status = 'active'
        flash('⚡ ¡Plan TechHelp PRO activado en modo desarrollo! Consultas ilimitadas desbloqueadas.', 'success')
    
    db.session.commit()
    return redirect(request.referrer or url_for('billing.pricing'))


@billing_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature', '')

    success, msg = handle_webhook_event(payload, sig_header)
    if success:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': msg}), 400
