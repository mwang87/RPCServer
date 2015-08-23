import os
import subprocess
import redis
from rq import Worker, Queue, Connection

listen = ['default']
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)



def execute_worker_task(input_parameters, output_folder, scratch_folder, zipped_result):
    result_output = custom_worker_task(input_parameters, output_folder, scratch_folder)

    #zipping up the output folder
    cmd = "tar -czvf " + zipped_result + " -C " + output_folder + " . "
    subprocess.call([cmd], shell=True)
    print cmd

    return result_output


def custom_worker_task(input_parameters, output_folder, scratch_folder):
    output_filename = os.path.join(output_folder, "ming.out")
    output_file = open(output_filename, "w")
    output_file.write("OutDummyFile.out")
    output_file.close()
    
    return "DUMMY CUSTOM WORKFLOW FINISHED"

    
if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()