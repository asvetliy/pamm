import asyncio


class Entrypoints:
    def __init__(self, type_, options_):
        self.type = type_
        self.options = options_

    def start(self, use_cases):
        if self.type == 'kafka_consumer':
            from .kafka_consumer import kafka_consumer
            threads_count = self.options.get('threads', None)
            threads = []
            if threads_count:
                loop = asyncio.get_event_loop()
                for i in range(0, threads_count):
                    task = loop.create_task(kafka_consumer(self, loop, use_cases))
                    threads.append(task)
                return threads
        else:
            print(f'{{"type": "entrypoints.error", "message": "unsupported entrypoint type: {self.type}"}}')
