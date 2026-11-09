from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for
from flask_login import login_required, current_user
from models import db, Conversation, Message
from services.ai_service import generate_ai_response, generate_conversation_title
from config import Config

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@login_required
def chat_view():
    conversations = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.updated_at.desc()).all()
    active_conversation = conversations[0] if conversations else None
    
    can_chat_flag, limit_msg = current_user.can_chat(Config.FREE_TIER_DAILY_LIMIT)
    
    return render_template(
        'chat/index.html',
        conversations=conversations,
        active_conversation=active_conversation,
        can_chat=can_chat_flag,
        limit_msg=limit_msg,
        free_limit=Config.FREE_TIER_DAILY_LIMIT
    )


@chat_bp.route('/chat/<int:conv_id>')
@login_required
def chat_conversation_view(conv_id):
    conv = Conversation.query.filter_by(id=conv_id, user_id=current_user.id).first_or_404()
    conversations = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.updated_at.desc()).all()
    
    can_chat_flag, limit_msg = current_user.can_chat(Config.FREE_TIER_DAILY_LIMIT)

    return render_template(
        'chat/index.html',
        conversations=conversations,
        active_conversation=conv,
        can_chat=can_chat_flag,
        limit_msg=limit_msg,
        free_limit=Config.FREE_TIER_DAILY_LIMIT
    )


@chat_bp.route('/api/conversations', methods=['GET', 'POST'])
@login_required
def api_conversations():
    if request.method == 'GET':
        conversations = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.updated_at.desc()).all()
        return jsonify([c.to_dict() for c in conversations])

    # POST: Crear nueva conversación
    title = request.json.get('title', 'Nueva incidencia técnica') if request.is_json else 'Nueva incidencia técnica'
    conv = Conversation(user_id=current_user.id, title=title)
    db.session.add(conv)
    db.session.commit()
    return jsonify(conv.to_dict()), 201


@chat_bp.route('/api/conversations/<int:conv_id>', methods=['DELETE'])
@login_required
def api_delete_conversation(conv_id):
    conv = Conversation.query.filter_by(id=conv_id, user_id=current_user.id).first_or_404()
    db.session.delete(conv)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Conversación eliminada con éxito'})


@chat_bp.route('/api/chat/<int:conv_id>/messages', methods=['GET'])
@login_required
def api_get_messages(conv_id):
    conv = Conversation.query.filter_by(id=conv_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'conversation': conv.to_dict(),
        'messages': [m.to_dict() for m in conv.messages]
    })


@chat_bp.route('/api/chat/<int:conv_id>/send', methods=['POST'])
@login_required
def api_send_message(conv_id):
    conv = Conversation.query.filter_by(id=conv_id, user_id=current_user.id).first_or_404()
    data = request.get_json() or {}
    user_text = data.get('message', '').strip()

    if not user_text:
        return jsonify({'error': 'El mensaje no puede estar vacío.'}), 400

    # Comprobar límite de plan
    can_chat, reason = current_user.can_chat(Config.FREE_TIER_DAILY_LIMIT)
    if not can_chat:
        return jsonify({
            'error': reason,
            'limit_reached': True
        }), 403

    # Guardar mensaje del usuario
    user_msg = Message(
        conversation_id=conv.id,
        sender='user',
        content=user_text
    )
    db.session.add(user_msg)
    
    # Actualizar contador de uso
    current_user.record_chat_query()

    # Actualizar título si es el primer mensaje o tiene título genérico
    if conv.title in ['Nueva incidencia técnica', 'Nueva conversación'] or len(conv.messages) <= 1:
        conv.title = generate_conversation_title(user_text)

    # Generar respuesta con IA
    try:
        reply_content = generate_ai_response(conv.messages, user_text)
    except Exception as e:
        reply_content = f"Disculpa, hubo un problema procesando tu incidencia: {str(e)}"

    assistant_msg = Message(
        conversation_id=conv.id,
        sender='assistant',
        content=reply_content
    )
    db.session.add(assistant_msg)
    
    db.session.commit()

    _, updated_limit_msg = current_user.can_chat(Config.FREE_TIER_DAILY_LIMIT)

    return jsonify({
        'reply': reply_content,
        'assistant_message': assistant_msg.to_dict(),
        'conversation_title': conv.title,
        'limit_msg': updated_limit_msg,
        'daily_queries': current_user.daily_queries_count,
        'is_pro': current_user.is_pro()
    })
