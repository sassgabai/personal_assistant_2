import logging

def setup_logger():
    '''
    Initialize logger
    '''
    log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    )


def get_logger(name: str):
    '''
    Return the logger, so I wont have to start it in every page
    '''
    return logging.getLogger(__name__)

