import logging
import asyncio
import uvloop
import os

from argparse import ArgumentParser
from aiohttp import web
from pamm.config import Config
from pamm.core.use_cases.use_cases import UseCases
from pamm.rest.routes import routes


async def on_cleanup(app_):
    log.info('Closing repository connections...')
    await app_.repository.pool.close()
    # log.info('Canceling entrypoints tasks...')
    # for e in app_.entrypoints:
    #     if e['type'] == 'kafka':
    #         for t in e['threads']:
    #             t.cancel()


def init_config() -> Config:
    parser = ArgumentParser(description='Pamm Service')
    parser.add_argument(
        '-config',
        dest='filepath',
        required=False,
        help='config file path (default is ./config/main.[json])',
        metavar='./PATH/TO/FILE or $HOME/app/<FILE>.json',
        default=None
    )
    parsed_args = parser.parse_args()
    if parsed_args.filepath is not None:
        if not os.path.isfile(parsed_args.filepath):
            config_ = Config()
            log.warning(f'The file [{parsed_args.filepath}] does not exist!')
            return config_
        else:
            try:
                return Config(parsed_args.filepath)
            except Exception as e:
                log.exception(e, exc_info=False)
    return Config()


async def init_app(config_: Config) -> web.Application:
    repository = await config_.repo.make()
    use_cases = UseCases.make(repository)
    entrypoints = []

    for e in config_.entrypoints:
        t = e.start(use_cases)
        entrypoints.append({'type': e.type, 'threads': t})

    app_ = web.Application()
    app_.on_cleanup.append(on_cleanup)

    for route in routes:
        app_.router.add_route(route[0], route[1], route[2])

    app_.config = config_
    app_.repository = repository
    app_.use_cases = use_cases
    app_.entrypoints = entrypoints

    return app_


if __name__ == '__main__':
    log = logging.getLogger(__name__)
    uvloop.install()
    loop = asyncio.get_event_loop()
    config = init_config()
    log.info('Starting...')
    app = loop.run_until_complete(init_app(config))
    web.run_app(app, port=config.config['service']['port'])
    log.info('Shutdown...')
