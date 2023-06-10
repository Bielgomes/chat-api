import communs 
from flask import request, abort, jsonify
from flask_restx import Resource, Namespace, fields

from endpoints.message_vo import MessageVO

from services.message_service import MessageService

ns = Namespace("chats", description="Chat API")

message_model = ns.add_model("message",
{
  "id": fields.Integer(required=True, description="Message Id"),
  "id_user": fields.Integer(required=True, description="User Id"),
  "id_chat": fields.Integer(required=True, description="Chat Id"),
  "date": fields.DateTime(required=True, description="Date"),
  "message": fields.String(required=True, description="Message", validate=lambda val: len(val) <= 400)
})

@ns.route("/<int:chat_id>/messages")
class MessagesEndpoint(Resource):
  __message_service = MessageService()

  def get(self, chat_id):
    token = request.headers.get("Authorization")
    if token is None or not len(token) == 36:
      abort(403, "Invalid Token")
      
    try:
      messages = self.__message_service.find_all_messages_from_chat(chat_id, token)
      messages = communs._to_json(messages)
    except IndexError as e:
      abort(404, e)

    return messages

  def post(self, chat_id):
    token = request.headers.get("Authorization")
    if token is None or not len(token) == 36:
      abort(403, "Invalid Token")
      
    body = request.get_json()

    try:
      message = MessageVO()
      message.from_json(body)
      self.__message_service.add_message(chat_id, message, token)
    except ValueError as e:
      abort(400, e)
    except IndexError as e:
      abort(404, e)
    except Exception as e:
      abort(409, e)

    return jsonify(success="Message created successfully")

@ns.route("/<int:chat_id>/messages/<int:message_id>")
class MessageEndpoint(Resource):
  __message_service = MessageService()

  def delete(self, chat_id, message_id):
    token = request.headers.get("Authorization")
    if token is None or not len(token) == 36:
      abort(403, "Invalid Token")

    try:
      self.__message_service.remove_message(chat_id, message_id, token)
    except IndexError as e:
      abort(404, e)
    except Exception as e:
      abort(403, e)

    return jsonify(success="Message deleted successfully")