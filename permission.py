import json
import sys
import uuid

from dbmodels import Event as DBEvent


class Event:
    name = 'GeneralEvent'
    aggregation_id = ''

    def move_to_storage(self, db_conn, with_data=True):
        db_event = DBEvent.create(
            type=self.name,
            data=json.dumps(self.get_data(with_data)),
            aggregation_id=self.aggregation_id
        )
        db_conn.add(db_event)
        db_conn.commit()

        if not self.aggregation_id:
            self.aggregation_id = uuid.UUID(db_event.aggregation_id)

    @classmethod
    def get_from_storage(self, db_conn, aggregation_id):
        return db_conn.query(DBEvent).filter(DBEvent.aggregation_id == str(aggregation_id)).all()


class PermissionEvent(Event):
    name = 'PermissionEvent'

    @classmethod
    def validate_value(cls, permission_value):
        if permission_value not in (True, False):
            raise ValueError('TODO')

    def get_data(self, with_data):
        if not with_data:
            return {}

        return {
            'permission_name': self.permission_name,
            'resource_type': self.resource_type,
            'permission_value': self.permission_value
        }


class PermissionCreated(PermissionEvent):
    name = 'PermissionCreated'

    def __init__(self, permission_name, resource_type, permission_value):
        self.permission_name = permission_name
        self.resource_type = resource_type
        self.permission_value = permission_value


class PermissionUpdated(PermissionEvent):
    name = 'PermissionUpdated'

    def __init__(self, permission_name, resource_type, permission_value):
        self.permission_name = permission_name
        self.resource_type = resource_type
        self.permission_value = permission_value


class PermissionDeleted(PermissionEvent):
    name = 'PermissionDeleted'

    def __init__(self, aggregation_id):
        self.aggregation_id = aggregation_id


class CommandManager:
    
    @classmethod
    def create_permission(cls, db_conn, permission_name, resource_type, permission_value):
        PermissionEvent.validate_value(permission_value)  # validate value
        permission_event = PermissionCreated(permission_name, resource_type, permission_value)  # create abstract obj
        permission_event.move_to_storage(db_conn)
        return permission_event
    
    @classmethod
    def update_permission(cls, db_conn, aggregation_id, permission_name, resource_type, permission_value):
        PermissionEvent.validate_value(permission_value)
        permission_event = PermissionUpdated(permission_name, resource_type, permission_value)
        permission_event.aggregation_id = aggregation_id
        permission_event.move_to_storage(db_conn)
        return permission_event
    
    @classmethod
    def delete_permission(cls, db_conn, aggregation_id):
        permission_event = PermissionDeleted(aggregation_id)
        permission_event.aggregation_id = aggregation_id
        permission_event.move_to_storage(db_conn, with_data=False)
        return permission_event


class Permission:
    # name
    # resource_type
    # value
    # aggregation_id

    def __init__(self, events):
        self.set_empty()

        for event in events:
            self.apply(event)

    def set_empty(self):
        self.permission_name = ''
        self.resource_type = ''
        self.permission_value = ''
        self.is_active = False

    def get_data(self):
        return {
            'permission_name': self.permission_name,
            'resource_type': self.resource_type,
            'permission_value': self.permission_value
        }

    def apply(self, event):
        event.data = json.loads(event.data)

        if event.type == PermissionCreated.name:
            self.permission_name = event.data['permission_name']
            self.resource_type = event.data['resource_type']
            self.permission_value = event.data['permission_value']
            self.is_active = True
        elif event.type == PermissionUpdated.name:
            if event.data.get('permission_name', ''):
                self.permission_name = event.data.get('permission_name')
            if event.data.get('resource_type', ''):
                self.resource_type = event.data.get('resource_type')
            if event.data.get('permission_value', ''):
                self.permission_value = event.data.get('permission_value')
            self.is_active = self.is_active or True
        elif event.type == PermissionDeleted.name:
            self.set_empty()
        else:
            raise ValueError('TODO')


class PermissionManager:

    @classmethod
    def get_permission(cls, db_conn, aggregation_id):
        events = Event.get_from_storage(db_conn, aggregation_id)
        permission = Permission(events)
        if permission.is_active:
            return permission.get_data()
        else:
            return None
