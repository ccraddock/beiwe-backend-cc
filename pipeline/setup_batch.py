"""
A script for setting up an AWS environment to run the Beiwe Data Access Pipeline
"""
#import ami_script
import docker_script
#import job_queue_script


if __name__ == '__main__':
    repo_uri = docker_script.run()
    #ami_id = ami_script.run()
    repo_uri = '476402459683.dkr.ecr.us-east-1.amazonaws.com/data-pipeline-docker'
    #ami_id = 'ami-083108e9d8ce5265d'
    #job_queue_script.run(repo_uri, ami_id)
