class groups:

    @staticmethod
    def principal(location=None, group=None):
        """
        Generates the principal name used internally by this application
        Supported keyword parameters are:
            site --  The site code
            group -- The group name
        """
        return location.name + ':' + group if location else group

    @staticmethod
    def administrator():
        return groups.principal(group='administrator')

    @staticmethod
    def manager():
        return groups.principal(group='manager')

    @staticmethod
    def reviewer(location=None):
        return groups.principal(group='reviewer')

    @staticmethod
    def member(location=None):
        return groups.principal(group='member')
