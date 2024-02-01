'''Example #1'''
import os
import logging
from dotenv import load_dotenv

from p0_client import run_check_and_remediation

load_dotenv()

logging.basicConfig( level=logging.INFO)
logger=logging.getLogger()
logger.setLevel(logging.INFO)

def run():
    '''Example Runner code for the snowflake_rest_state_client'''
    logger.info('Started') 
    run_check_and_remediation(os.environ.get('P0_TENANT_ID'),
                              os.environ.get('P0_TOKEN'))
    logger.info('Finished')

if __name__ == '__main__':
    run()
