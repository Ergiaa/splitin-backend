from datetime import datetime
from models import Bill, Groups, Items, Assignments, Participants, Payments, Ledgers, User
from utils.error import CustomError
from flask import g as ctx
from utils.clean import clean_datetime

class GroupService:
    def create_group(self, data):
        ref = Groups.create_ref()

        members = data.get('members', [])

        if (ctx.user_id not in members) and ctx.user_id:
            members.append(ctx.user_id)

        data = {
            'name': data.get('name', 'New Group'),
            'created_by': ctx.user_id,
            'members': members,
        }

        ref.set(data)

        return ref.get().to_dict()

    def get_group(self, group_id):
        group = Groups(group_id)
        data = group.get()

        if not data:
            raise CustomError("group not found", 404)
        
        bills = Bill.get_all_by_group(group_id)

        for member in data.get('members', []):
            user = User(member).get()
            if user:
                member_data = {
                    'id': user['id'],
                    'username': user.get('username', ''),
                    'email': user.get('email', ''),
                    'phone_number': user.get('phone_number', '')
                }
                data['members'][data['members'].index(member)] = member_data


        data['bills'] = bills

        return data
    
    def get_all_groups(self, user_id=None):
        user_id = user_id or ctx.user_id

        groups = Groups.get_all(user_id)

        if not groups:
            raise CustomError("no groups found", 404)

        return groups

    def join_group(self, group_id, user_id=None):
        ref = Groups(group_id)
        data = ref.get()

        if not data:
            raise CustomError("group not found", 404)

        members = data.get('members', [])

        if data.get('created_by') != ctx.user_id:
            raise CustomError("not creator of group", 401)

        join_user_id = user_id or ctx.user_id

        if join_user_id in members:
            raise CustomError("user already joined the group", 400)

        members.append(join_user_id)

        ref.update({'members': members})

        data['members'] = members

        return data
