from dbmodels import Event as DBEvent


class Event:
    name = 'GeneralEvent'

    def move_to_storage(self):
        return DBEvent.create(type=self.name, data=self.get_data(), aggregation_id=self.aggregation_id)

    @classmethod
    def get_from_storage(self, aggregation_id):
        return DBEvent.filter(aggregation_id=self.aggregation_id)  # TODO: call db select


class PermissionEvent(Event):
    name = 'PermissionEvent'

    @classmethod
    def validate_value(cls, permission_value):
        if permission_value not in (True, False):
            raise ValueError('TODO')

    def gen_aggregation_id(self):
        self.aggregation_id = '{}_{}'.format(self.name, self.resource_type)

    def get_data(self):
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
    def create_permission(cls, permission_name, resource_type, permission_value):
        PermissionEvent.validate_value(permission_value)  # validate value
        permission_event = PermissionCreated(permission_name, resource_type, permission_value)  # create abstract obj
        return permission_event.move_to_storage()
    
    @classmethod
    def update_permission(cls, permission_name, resource_type, permission_value):
        PermissionEvent.validate_value(permission_value)
        permission_event = PermissionUpdated(permission_name, resource_type, permission_value)
        return permission_event.move_to_storage()
    
    @classmethod
    def delete_permission(cls, aggregation_id):
        permission_event = PermissionDeleted(aggregation_id)
        return permission_event.move_to_storage()


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
