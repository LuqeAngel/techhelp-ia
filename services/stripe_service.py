import logging
import stripe
from config import Config
from models import db, User

logger = logging.getLogger(__name__)

stripe.api_key = Config.STRIPE_SECRET_KEY

def is_stripe_configured():
    return bool(Config.STRIPE_SECRET_KEY and not Config.STRIPE_SECRET_KEY.startswith("sk_test_tu_clave"))

def create_checkout_session(user: User, success_url: str, cancel_url: str):
    """
    Crea una sesión de Checkout en Stripe para el plan Pro mensual.
    Si Stripe no está configurado, retorna None para usar el flujo simulado.
    """
    if not is_stripe_configured():
        return None

    try:
        stripe.api_key = Config.STRIPE_SECRET_KEY
        
        # Buscar o crear cliente si ya tiene stripe_customer_id
        customer_kwargs = {}
        if user.stripe_customer_id:
            customer_kwargs['customer'] = user.stripe_customer_id
        else:
            customer_kwargs['customer_email'] = user.email

        # Si hay un Price ID configurado que comience por price_, lo usamos;
        # si no, creamos el precio dinámicamente con price_data (19€/mes).
        if Config.STRIPE_PRICE_ID_PRO and Config.STRIPE_PRICE_ID_PRO.startswith("price_"):
            line_items = [{
                'price': Config.STRIPE_PRICE_ID_PRO,
                'quantity': 1,
            }]
        else:
            line_items = [{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'TechHelp Pro Mensual',
                        'description': 'Consultas ilimitadas 24/7 y soporte informático con IA',
                    },
                    'unit_amount': 1900, # 19.00 EUR
                    'recurring': {'interval': 'month'},
                },
                'quantity': 1,
            }]

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='subscription',
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            client_reference_id=str(user.id),
            metadata={
                'user_id': str(user.id),
                'user_email': user.email
            },
            **customer_kwargs
        )
        return checkout_session.url
    except Exception as e:
        logger.exception(f"Error creando sesión de Stripe Checkout: {e}")
        return None


def handle_webhook_event(payload: bytes, sig_header: str):
    """
    Procesa webhooks entrantes de Stripe para activar o cancelar suscripciones.
    """
    if not is_stripe_configured():
        return False, "Stripe no configurado"

    try:
        if Config.STRIPE_WEBHOOK_SECRET and not Config.STRIPE_WEBHOOK_SECRET.startswith("whsec_tu_webhook"):
            event = stripe.Webhook.construct_event(
                payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
            )
        else:
            # En pruebas locales sin verificación estricta de firma
            event = stripe.Event.construct_from(
                stripe.util.json.loads(payload.decode('utf-8')), stripe.api_key
            )
    except ValueError as e:
        logger.error(f"Payload inválido de Stripe webhook: {e}")
        return False, "Invalid payload"
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Firma de Stripe webhook inválida: {e}")
        return False, "Invalid signature"

    event_type = event['type']
    data_object = event['data']['object']

    logger.info(f"Stripe Webhook recibido: {event_type}")

    if event_type == 'checkout.session.completed':
        user_id = data_object.get('client_reference_id') or data_object.get('metadata', {}).get('user_id')
        customer_id = data_object.get('customer')
        subscription_id = data_object.get('subscription')

        if user_id:
            user = User.query.get(int(user_id))
            if user:
                user.subscription_tier = 'pro'
                user.subscription_status = 'active'
                user.stripe_customer_id = customer_id
                user.stripe_subscription_id = subscription_id
                db.session.commit()
                logger.info(f"Usuario {user.email} actualizado exitosamente a PRO.")

    elif event_type in ['customer.subscription.updated', 'customer.subscription.created']:
        sub_id = data_object.get('id')
        status = data_object.get('status') # 'active', 'past_due', 'canceled'
        customer_id = data_object.get('customer')

        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.stripe_subscription_id = sub_id
            user.subscription_status = status
            if status == 'active':
                user.subscription_tier = 'pro'
            else:
                user.subscription_tier = 'free'
            db.session.commit()
            logger.info(f"Suscripción de {user.email} actualizada a {status}")

    elif event_type == 'customer.subscription.deleted':
        customer_id = data_object.get('customer')
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.subscription_tier = 'free'
            user.subscription_status = 'canceled'
            db.session.commit()
            logger.info(f"Suscripción cancelada para usuario {user.email}")

    return True, "Success"


def create_portal_session(user: User, return_url: str):
    """Genera URL para que el usuario gestione o cancele su suscripción en Stripe."""
    if not is_stripe_configured() or not user.stripe_customer_id:
        return None
    try:
        stripe.api_key = Config.STRIPE_SECRET_KEY
        portal_session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=return_url
        )
        return portal_session.url
    except Exception as e:
        logger.exception(f"Error creando Billing Portal Session: {e}")
        return None
