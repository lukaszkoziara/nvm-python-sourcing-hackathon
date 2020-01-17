class Event:
    name = 'GeneralEvent'

    def generate_uuid(self):
        pass  # TODO: generate

    def move_to_storage(self):
        self.generate_uuid()
        # TODO: call db insert


class PermissionEvent(Event):
    name = 'PermissionEvent'

    @classmethod
    def validate_value(cls, permission_value):
        if permission_value not in (True, False):
            raise ValueError('TODO')

    def gen_aggregation_id(self):
        self.aggregation_id = '{}_{}'.format(self.name, self.resource_type)


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

    def __init__(self, permission_name, resource_type):
        self.permission_name = permission_name


class CommandManager:

    @classmethod
    def create_permission(cls, permission_name, resource_type, permission_value):
        PermissionEvent.validate_value(permission_value)  # validate value
        permission_event = PermissionCreated(permission_name, resource_type, permission_value)  # create abstract obj
        # TODO: validate operation - (exists & not deleted)
        # TODO: publish event to store

    @classmethod
    def update_permission(cls, permission_id, permission_value):
        if permission_value not in (True, False):
            raise ValueError('TODO')

        # TODO: validate value
        permission = None  # TODO: get data
        event = PermissionUpdated(permission.name, permission.resource_type, permission_value)
        # TODO: publish event to store

    @classmethod
    def delete_permission(cls, permission_id):
        pass
        # TODO: publish event to store


class Permission:
    # name
    # resource_type
    # value
    # id

    def __init__(self, events):
        for event in events:
            self.apply(event)

        self.changes = []

    @classmethod
    def create(cls, permission_name, permission_value):
        initial_event = PermissionCreated(permission_name, permission_value)
        instance = cls([initial_event])
        instance.changes = [initial_event]
        return instance

    def apply(self, event):
        if isinstance(event, PermissionCreated):
            self.permission_name = event.permission_name
            self.permission_value = event.permission_value
        elif isinstance(event, PermissionUpdated):
            self.permission_name = event.permission_name
            self.permission_value = event.permission_value
        elif isinstance(event, PermissionDeleted):
            pass
        else:
            raise ValueError('TODO')

    def store_to_storage(self):
        pass

    # def update_permission(self, permission_name, permission_value):
    #     if permission_name not in ('TODO: something'):
    #         raise ValueError('TODO')
    #
    #     if permission_value not in (True, False):
    #         raise ValueError('Insufficient action type')
    #
    #     event = PermissionUpdated(permission_name, permission_value)
    #     self.apply(event)
    #     self.changes.append(event)
