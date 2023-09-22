# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.utils import calculate_cost
from user.models import User
from chat.models import BroadcastPermission, BroadcastPlan, Conversation, ChatMessage




class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            self.user = self.scope['user']
            await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        received_data = json.loads(text_data)
        action = received_data.get('action')
        message = received_data.get('message')
        conversation_id = received_data.get('conversation_id')

        if action == 'create':
            await self.create_conversation(received_data)
        elif action == 'delete-message':
            await self.delete_message(conversation_id, message)
        elif action == 'add_participant':
            await self.add_participant(received_data)
        elif action == 'remove_participant':
            await self.remove_participant(received_data)
        elif action == 'archive':
            await self.archive_conversation(received_data)
        elif action == 'unarchive':
            await self.unarchive_conversation(received_data)
        elif action == 'message':
            await self.send_message(conversation_id, message)
        elif action == 'assign_role':
            await self.assign_role(received_data)
        elif action == 'change_member_role':
            await self.change_member_role(received_data)
        elif action == 'set_message_visibility':
            await self.set_message_visibility(received_data)
        elif action == 'add_visible_to':
            await self.add_visible_to(received_data)
        elif action == 'remove_visible_to':
            await self.remove_visible_to(received_data)
        elif action == 'add_read_only_participant':
            await self.add_read_only_participant(received_data)
        elif action == 'remove_read_only_participant':
            await self.remove_read_only_participant(received_data)
        elif action == 'report_message':
            await self.report_message(received_data)
        elif action == 'star_message':
            await self.star_message(received_data)
        elif action == 'forward_message':
            await self.forward_message(received_data)
        elif action == 'block_user':
            await self.block_user(received_data)  # Handle user blocking
        elif action == 'unblock_user':
            await self.unblock_user(received_data)  # Handle user unblocking
        elif action == 'broadcast_message':
            await self.send_broadcast_message(message)  # Handle broadcast message

    async def chat_message(self, event):
        await self.send(text_data=event['text'])

    async def send_error_message(self, message):
        response = {
            'error': message
        }
        await self.send(text_data=json.dumps(response))

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            return conversation
        except Conversation.DoesNotExist:
            return None

    @database_sync_to_async
    def create_conversation(self, data):
        participants = data.get('participants')
        group_name = data.get('group_name')
        is_group = True if len(participants) > 2 else False

        conversation = Conversation.objects.create(
            group_name=group_name, is_group=is_group)
        conversation.participants.add(*participants)
        conversation.save()

        response = {
            'action': 'created',
            'conversation_id': conversation.id
        }
        self.send(text_data=json.dumps(response))

    @database_sync_to_async
    def add_participant(self, data):
        conversation = self.get_conversation(data.get('conversation_id'))
        if conversation:
            participant = data.get('participant')
            conversation.participants.add(participant)
            conversation.save()

    @database_sync_to_async
    def remove_participant(self, data):
        conversation = self.get_conversation(data.get('conversation_id'))
        if conversation:
            participant = data.get('participant')
            conversation.participants.remove(participant)
            conversation.save()

    @database_sync_to_async
    def archive_conversation(self, data):
        conversation = self.get_conversation(data.get('conversation_id'))
        if conversation:
            conversation.is_archived = True
            conversation.save()

    @database_sync_to_async
    def unarchive_conversation(self, data):
        conversation = self.get_conversation(data.get('conversation_id'))
        if conversation:
            conversation.is_archived = False
            conversation.save()

    async def send_message(self, conversation_id, message):
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            if self.user not in conversation.participants.all():
                await self.send_error_message('You are not a participant in this conversation')
                return

            await self.create_chat_message(conversation, self.user, message)

            response = {
                'action': 'message',
                'message': message,
                'sent_by': self.user.id,
                'conversation_id': conversation_id
            }

            await self.channel_layer.group_send(
                conversation_id,
                {
                    'type': 'chat_message',
                    'text': json.dumps(response)
                }
            )

    @database_sync_to_async
    def create_chat_message(self, conversation, user, msg):
        ChatMessage.objects.create(
            conversation=conversation, user=user, message=msg)

    # Implementations for assign_role, change_member_role, set_message_visibility,
    # add_visible_to, remove_visible_to, add_read_only_participant, remove_read_only_participant,
    # report_message, star_message, and forward_message actions
    async def assign_role(self, data):
        # Implement the logic to assign a role to a participant
        conversation = await self.get_conversation(data.get('conversation_id'))
        if conversation:
            participant_id = data.get('participant_id')
            role = data.get('role')

            if not participant_id or not role:
                await self.send_error_message('Participant ID and role are required.')
                return

            try:
                participant = User.objects.get(id=participant_id)
            except User.DoesNotExist:
                await self.send_error_message('Participant not found.')
                return

            # Ensure that the request user is the owner of the conversation or an admin
            user_role = conversation.roles.get(str(self.user.id))
            if user_role not in ['owner', 'admin']:
                await self.send_error_message('You do not have permission to assign roles.')
                return

            # Validate the role being assigned
            if role not in ['admin', 'moderator', 'participant']:
                await self.send_error_message('Invalid role.')
                return

            # Assign the role to the participant
            conversation.roles[str(participant.id)] = role
            conversation.save()

            serializer = self.get_serializer(conversation)
            await self.send(text_data=json.dumps(serializer.data))

    async def change_member_role(self, data):
        # Implement the logic to change the role of a member
        conversation = await self.get_conversation(data.get('conversation_id'))
        if conversation:
            member_id = data.get('member_id')
            new_role = data.get('new_role')

            if not member_id or not new_role:
                await self.send_error_message('Member ID and new role are required.')
                return

            try:
                member = User.objects.get(id=member_id)
            except User.DoesNotExist:
                await self.send_error_message('Member not found.')
                return

            # Ensure that the request user is the owner of the conversation or an admin
            user_role = conversation.roles.get(str(self.user.id))
            if user_role not in ['owner', 'admin']:
                await self.send_error_message('You do not have permission to change member roles.')
                return

            # Validate the new role being assigned
            if new_role not in ['admin', 'moderator', 'participant']:
                await self.send_error_message('Invalid new role.')
                return

            # Change the role of the member
            conversation.roles[str(member.id)] = new_role
            conversation.save()

            serializer = self.get_serializer(conversation)
            await self.send(text_data=json.dumps(serializer.data))

    async def set_message_visibility(self, data):
        # Implement the logic to set message visibility
        conversation = await self.get_conversation(data.get('conversation_id'))
        if conversation:
            message_id = data.get('message_id')
            visibility = data.get('visibility', 'default')

            if not message_id or visibility not in ['default', 'custom']:
                await self.send_error_message('Invalid request data.')
                return

            try:
                # Retrieve the message based on message_id
                message = ChatMessage.objects.get(
                    id=message_id, thread__id=conversation.id)
            except ChatMessage.DoesNotExist:
                await self.send_error_message('Message not found.')
                return

            # Ensure that the request user is a participant in the conversation
            if self.user not in conversation.participants.all():
                await self.send_error_message('You are not a participant in this conversation.')
                return

            # Check if the user has permission to set custom visibility
            user_role = conversation.roles.get(str(self.user.id))

            # Participants can set custom visibility for their own messages
            if visibility == 'custom':
                if user_role not in ['owner', 'admin', 'moderator', 'participant']:
                    await self.send_error_message('You do not have permission to set custom visibility.')
                    return

            # Set the message-specific visibility flag
            message.custom_visibility = (visibility == 'custom')
            message.save()

            serializer = self.get_serializer(conversation)
            await self.send(text_data=json.dumps(serializer.data))

    async def add_visible_to(self, data):
        # Implement the logic to add a participant as a user who can see the message
        conversation = await self.get_conversation(data.get('conversation_id'))
        if conversation:
            message_id = data.get('message_id')
            participant_id = data.get('participant_id')

            if not message_id or not participant_id:
                await self.send_error_message('Invalid request data.')
                return

            try:
                # Retrieve the message based on message_id
                message = ChatMessage.objects.get(
                    id=message_id, thread__id=conversation.id)
            except ChatMessage.DoesNotExist:
                await self.send_error_message('Message not found.')
                return

            # Ensure that the request user is a participant in the conversation
            if self.user not in conversation.participants.all():
                await self.send_error_message('You are not a participant in this conversation.')
                return

            # Check if the user has permission to add users who can see the message
            user_role = conversation.roles.get(str(self.user.id))

            # Participants can add users who can see their own messages
            if user_role not in ['owner', 'admin', 'moderator', 'participant']:
                await self.send_error_message('You do not have permission to add users who can see the message.')
                return

            # Add the participant as a user who can see the message
            try:
                participant = User.objects.get(id=participant_id)
                message.visible_to.add(participant)
                message.save()
            except User.DoesNotExist:
                await self.send_error_message('Participant not found.')
                return

            serializer = self.get_serializer(conversation)
            await self.send(text_data=json.dumps(serializer.data))

    async def remove_visible_to(self, data):
        # Implement the logic to remove a participant from the users who can see the message
        conversation = await self.get_conversation(data.get('conversation_id'))
        if conversation:
            message_id = data.get('message_id')
            participant_id = data.get('participant_id')

            if not message_id or not participant_id:
                await self.send_error_message('Invalid request data.')
                return

            try:
                # Retrieve the message based on message_id
                message = ChatMessage.objects.get(
                    id=message_id, thread__id=conversation.id)
            except ChatMessage.DoesNotExist:
                await self.send_error_message('Message not found.')
                return

            # Ensure that the request user is a participant in the conversation
            if self.user not in conversation.participants.all():
                await self.send_error_message('You are not a participant in this conversation.')
                return

            # Check if the user has permission to remove users who can see the message
            user_role = conversation.roles.get(str(self.user.id))

            # Participants can remove users who can see their own messages
            if user_role not in ['owner', 'admin', 'moderator', 'participant']:
                await self.send_error_message('You do not have permission to remove users who can see the message.')
                return

            # Remove the participant from the users who can see the message
            try:
                participant = User.objects.get(id=participant_id)
                message.visible_to.remove(participant)
                message.save()
            except User.DoesNotExist:
                await self.send_error_message('Participant not found.')
                return

            serializer = self.get_serializer(conversation)
            await self.send(text_data=json.dumps(serializer.data))

    async def add_read_only_participant(self, data):
        # Implement the logic to add a participant as a read-only participant for the message
        conversation = await self.get_conversation(data.get('conversation_id'))
        if conversation:
            message_id = data.get('message_id')
            participant_id = data.get('participant_id')

            if not message_id or not participant_id:
                await self.send_error_message('Invalid request data.')
                return

            try:
                # Retrieve the message based on message_id
                message = ChatMessage.objects.get(
                    id=message_id, thread__id=conversation.id)
            except ChatMessage.DoesNotExist:
                await self.send_error_message('Message not found.')
                return

            # Ensure that the request user is a participant in the conversation
            if self.user not in conversation.participants.all():
                await self.send_error_message('You are not a participant in this conversation.')
                return

            # Check if the user has permission to add read-only participants
            user_role = conversation.roles.get(str(self.user.id))
            if user_role not in ['owner', 'admin', 'moderator']:
                await self.send_error_message('You do not have permission to add read-only participants.')
                return

            # Add the participant as a read-only participant for the message
            try:
                participant = User.objects.get(id=participant_id)
                message.read_only_participants.add(participant)
                message.save()
            except User.DoesNotExist:
                await self.send_error_message('Participant not found.')
                return

            serializer = self.get_serializer(conversation)
            await self.send(text_data=json.dumps(serializer.data))

    async def remove_read_only_participant(self, data):
        # Implement the logic to remove a participant from the read-only participants of the message
        conversation = await self.get_conversation(data.get('conversation_id'))
        if conversation:
            message_id = data.get('message_id')
            participant_id = data.get('participant_id')

            if not message_id or not participant_id:
                await self.send_error_message('Invalid request data.')
                return

            try:
                # Retrieve the message based on message_id
                message = ChatMessage.objects.get(
                    id=message_id, thread__id=conversation.id)
            except ChatMessage.DoesNotExist:
                await self.send_error_message('Message not found.')
                return

            # Ensure that the request user is a participant in the conversation
            if self.user not in conversation.participants.all():
                await self.send_error_message('You are not a participant in this conversation.')
                return

            # Check if the user has permission to remove read-only participants
            user_role = conversation.roles.get(str(self.user.id))
            if user_role not in ['owner', 'admin', 'moderator']:
                await self.send_error_message('You do not have permission to remove read-only participants.')
                return

            # Remove the participant from the read-only participants of the message
            try:
                participant = User.objects.get(id=participant_id)
                message.read_only_participants.remove(participant)
                message.save()
            except User.DoesNotExist:
                await self.send_error_message('Participant not found.')
                return

            serializer = self.get_serializer(conversation)
            await self.send(text_data=json.dumps(serializer.data))

    async def report_message(self, data):
        # Implement the logic to report a message
        conversation = await self.get_conversation(data.get('conversation_id'))
        if conversation:
            message_id = data.get('message_id')

            if not message_id:
                await self.send_error_message('Invalid request data.')
                return

            try:
                # Retrieve the message based on message_id
                message = ChatMessage.objects.get(
                    id=message_id, thread__id=conversation.id)
            except ChatMessage.DoesNotExist:
                await self.send_error_message('Message not found.')
                return

            # Ensure that the request user is a participant in the conversation
            if self.user not in conversation.participants.all():
                await self.send_error_message('You are not a participant in this conversation.')
                return

            # Mark the message as reported
            message.is_reported = True
            message.save()

            serializer = self.get_serializer(conversation)
            await self.send(text_data=json.dumps(serializer.data))

    async def star_message(self, data):
        # Implement the logic to star a message
        conversation = await self.get_conversation(data.get('conversation_id'))
        if conversation:
            message_id = data.get('message_id')

            if not message_id:
                await self.send_error_message('Invalid request data.')
                return

            try:
                # Retrieve the message based on message_id
                message = ChatMessage.objects.get(
                    id=message_id, thread__id=conversation.id)
            except ChatMessage.DoesNotExist:
                await self.send_error_message('Message not found.')
                return

            # Ensure that the request user is a participant in the conversation
            if self.user not in conversation.participants.all():
                await self.send_error_message('You are not a participant in this conversation.')
                return

            # Mark the message as starred
            message.is_starred = True
            message.save()

            serializer = self.get_serializer(conversation)
            await self.send(text_data=json.dumps(serializer.data))

    async def forward_message(self, data):
        # Implement the logic to forward a message to another conversation
        conversation = await self.get_conversation(data.get('conversation_id'))
        if conversation:
            message_id = data.get('message_id')
            target_conversation_id = data.get('target_conversation_id')

            if not message_id or not target_conversation_id:
                await self.send_error_message('Invalid request data.')
                return

            try:
                # Retrieve the message based on message_id
                message = ChatMessage.objects.get(
                    id=message_id, thread__id=conversation.id)
            except ChatMessage.DoesNotExist:
                await self.send_error_message('Message not found.')
                return

            # Ensure that the request user is a participant in the conversation
            if self.user not in conversation.participants.all():
                await self.send_error_message('You are not a participant in this conversation.')
                return

            # Ensure that the target conversation exists
            try:
                target_conversation = Conversation.objects.get(
                    id=target_conversation_id)
            except Conversation.DoesNotExist:
                await self.send_error_message('Target conversation not found.')
                return

            # Check if the user has permission to forward messages
            user_role = conversation.roles.get(str(self.user.id))

            # Participants can forward messages
            if user_role not in ['owner', 'admin', 'moderator', 'participant']:
                await self.send_error_message('You do not have permission to forward messages.')
                return

            # Create a new message in the target conversation with the same content
            ChatMessage.objects.create(
                thread=target_conversation,
                user=self.user,
                message=message.message,
                is_private=message.is_private,
                is_public=message.is_public,
                custom_visibility=message.custom_visibility,
            )

            serializer = self.get_serializer(conversation)
            await self.send(text_data=json.dumps(serializer.data))

    # Private Chats
    @database_sync_to_async
    def block_user(self, data):
        conversation_id = data.get('conversation_id')
        user_to_block_id = data.get('user_to_block_id')

        try:
            conversation = Conversation.objects.get(id=conversation_id)
            user_to_block = User.objects.get(id=user_to_block_id)
        except (Conversation.DoesNotExist, User.DoesNotExist):
            return

        # Check if the user is a participant in the conversation
        if user_to_block not in conversation.participants.all():
            return

        # Add the user to the block list for the conversation
        conversation.blocked_users.add(user_to_block)
        conversation.save()

    @database_sync_to_async
    def unblock_user(self, data):
        conversation_id = data.get('conversation_id')
        user_to_unblock_id = data.get('user_to_unblock_id')

        try:
            conversation = Conversation.objects.get(id=conversation_id)
            user_to_unblock = User.objects.get(id=user_to_unblock_id)
        except (Conversation.DoesNotExist, User.DoesNotExist):
            return

        # Check if the user is a participant in the conversation
        if user_to_unblock not in conversation.participants.all():
            return

        # Remove the user from the block list for the conversation
        conversation.blocked_users.remove(user_to_unblock)
        conversation.save()

    @database_sync_to_async
    def send_broadcast_message(self, message_text, recipients):
        try:
            # Retrieve the broadcast conversation
            broadcast_conversation = Conversation.objects.get(group_name='broadcast')
        except Conversation.DoesNotExist:
            # Create the broadcast conversation if it doesn't exist
            broadcast_conversation = Conversation.objects.create(
                group_name='broadcast', is_group=True)
            # Add all users to the broadcast conversation
            all_users = User.objects.all()
            broadcast_conversation.participants.add(*all_users)
            broadcast_conversation.save()

        # Send the broadcast message to the conversation
        self.send_message(broadcast_conversation.id, message_text)

    @database_sync_to_async
    def delete_message(self, conversation_id, message_id):
        try:
            # Retrieve the message based on message_id
            message = ChatMessage.objects.get(id=message_id, thread__id=conversation_id)
        except ChatMessage.DoesNotExist:
            return

        # Mark the message as deleted
        message.is_deleted = True
        message.save()

        # Broadcast message plan
        
    # async def handle_broadcast_request(self, data):
    #     # Check if the user has purchased broadcast permissions
    #     try:
    #         broadcast_permission = BroadcastPermission.objects.get(user=self.user)
    #     except BroadcastPermission.DoesNotExist:
    #         await self.send_error_message("You haven't purchased broadcast permissions.")
    #         return

    #     # Check if the user has enough remaining recipients
    #     if broadcast_permission.remaining_recipients <= 0:
    #         await self.send_error_message("You have used all available recipients.")
    #         return

    #     # Calculate the cost based on the number of recipients and your pricing model
    #     num_recipients = data.get("num_recipients")
    #     cost = calculate_cost(num_recipients)  # Implement your pricing logic

    #     # Get the list of recipients from the request data
    #     recipient_ids = data.get("recipient_ids")
    #     recipients = User.objects.filter(id__in=recipient_ids)

    #     # Send the broadcast message
    #     await self.send_broadcast_message(data.get("message"), recipients)

    #     # Update remaining recipients count
    #     broadcast_permission.remaining_recipients -= num_recipients
    #     broadcast_permission.save()
