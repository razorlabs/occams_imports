import json


_CHANNEL = 'mapping'


class ImportStatusChannel(object):

    def __init__(self, redis, jobid, channel=_CHANNEL):
        self._redis = redis
        self._jobid = jobid
        self._channel = channel

    def send_reset(self, total_items):
        redis = self._redis
        jobid = self._jobid
        redis.hmset(jobid, {'count': 0, 'total': total_items})

    def send_progress(self):
        redis = self._redis
        jobid = self._jobid
        channel = self._channel

        redis.hincrby(jobid, 'count')

        # redis-py returns everything as string, so we need to clean it
        raw = redis.hgetall(jobid)
        data = {'count': int(raw['count']), 'total': int(raw['total'])}
        notification = json.dumps(data)
        print(notification)
        redis.publish(channel, notification)

    def send_message(self, mapping, message):
        redis = self._redis
        channel = self._channel

        data = {
            'schema': mapping.logic.get('target_schema'),
            'variable': mapping.logic.get('target_variable'),
            'message': message.format(mappings=mapping)
        }

        notification = json.dumps(data)
        print(notification)
        redis.publish(channel, notification)
