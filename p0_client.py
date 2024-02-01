"""This module provides a client for p0 service"""
import logging
import time
import requests

MAX_TIME_OUT_MINS=15*60

logger=logging.getLogger('snowflake_rest_state_client')
logger.setLevel(logging.INFO)

class UnauthorizedException(Exception):
    '''Exception raised for invalid authentication'''
class NotFoundException(Exception):
    '''Exception raised for invalid authentication'''
class DriftCheckFailedException(Exception):
    '''Exception raised for invalid authentication'''
class DriftRemediationFailedException(Exception):
    '''Exception raised for invalid authentication'''
class GenericResponseException(Exception):
    '''Exception raised for error in response'''
class JobErroredException(Exception):
    '''Exception raised for error in job'''

def rest_state_url(base_url,tenant_id):
    '''returns the rest state url for the tenant'''
    return f'{base_url}/{tenant_id}/iam/resource/rest-state/snowflake/v1/diff'
def process_result(response):
    '''processes the response and returns the result'''
    if response.status_code != 200:
        if response.status_code == 404:
            raise NotFoundException(response,"Not Found")
        elif response.status_code == 401:
            raise UnauthorizedException(response,"Unauthorized")
    if response.headers.get('content-type') != 'application/json':
        raise GenericResponseException(response,"Error in response")
    if 'error' in response.json():
        raise JobErroredException(response.json(),"Error in response")
    
    return response.json()
def snowflake_rest_state_client(base_url,tenant_id,token):
    """provides p0 client for rest state service"""
    def initiate_drift_check():
        '''initiates drift check  for the tenant'''
        response=requests.post(url=rest_state_url(base_url,tenant_id),
                             headers={'Authorization': f'Bearer {token}'},
                             timeout=10)
        try:
            response=process_result(response)
            logger.info("Initiated drift check  for tenant %s %s",
                        tenant_id,
                        response.json(),
                        extra={'response':response.json()})
            return response.json()
        except JobErroredException as exc:
            raise DriftCheckFailedException from exc
    def wait_till_job_completes(run_id):
        '''waits for the drift check job to complete'''        
        start_time = time.time()
        while True:
            if time.time() - start_time > (MAX_TIME_OUT_MINS):
                raise JobErroredException("Job is taking too long to complete")
            response=requests.get(url=rest_state_url(base_url,tenant_id)+ f'/{run_id}',
                                headers={'Authorization': f'Bearer {token}'},
                                timeout=10)
            try:
                response=process_result(response)
                logger.info("Waiting for %s to complete",
                        run_id,
                        extra={'response':response.json()})
                if response.json()['status'] != 'PROCESSING':
                    break
                time.sleep(3)
            except JobErroredException as exc:
                raise DriftCheckFailedException from exc
        return response.json()
    def initiate_drift_remediation(run_id):
        '''initiates drift remediation for the tenant for the given run id'''
        response=requests.post(url=rest_state_url(base_url,tenant_id) + f'/{run_id}/enforce',
                             headers={'Authorization': f'Bearer {token}'},
                             timeout=10)
        try:
            response=process_result(response)
            logger.info("Initiated Drift remediation for %s to complete",
                        run_id,
                        extra={'response':response.json()})
            return response.json()
        except JobErroredException as exc:
            raise DriftRemediationFailedException from exc
    return  initiate_drift_check, wait_till_job_completes, initiate_drift_remediation   
def run_check_and_remediation(base_url,tenant_id,token):
    '''runs the drift check and remediation'''
    initiate_drift_check, wait_till_job_completes, initiate_drift_remediation=snowflake_rest_state_client(base_url,tenant_id,token)
    try:
        drift_run_result=initiate_drift_check()
        drift_run_status=wait_till_job_completes(drift_run_result['runId'])
        if drift_run_status['status'] == 'SUCCESS':
            logger.info("Drift check completed successfully")
            initiate_drift_remediation(drift_run_result['runId'])
            wait_till_job_completes(drift_run_result['runId'])
            logger.info("Drift remediation completed successfully")
    except UnauthorizedException as e:
        logger.error("Please see if the token provided is still valid")
        raise e
    except NotFoundException as e:
        logger.error("Please see if the tenant and run id provided are still valid")
        raise e
    except GenericResponseException as e:
        logger.error("Invalid Response contact p0")
        raise e
