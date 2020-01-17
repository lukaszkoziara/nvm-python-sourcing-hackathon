import json
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
    def get_from_storage(self, aggregation_id):
        return DBEvent.filter(aggregation_id=self.aggregation_id)  # TODO: call db select


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
        for event in events:
            self.apply(event)

    def get_data(self):
        return {}

    def apply(self, event):
        if isinstance(event, PermissionCreated) or isinstance(event, PermissionUpdated):
            self.permission_name = event.permission_name
            self.resource_type = event.resource_type
            self.permission_value = event.permission_value
        elif isinstance(event, PermissionDeleted):
            pass  # TODO
        else:
            raise ValueError('TODO')


class PermissionManager:

    @classmethod
    def get_permission(self, aggregation_id):
        events = Event.get_from_storage(aggregation_id)
        return Permission(events).get_data()
