
import os
from flask import Flask, request, redirect, url_for, send_file

import random
import string
import json
import subprocess

import redis
from rq import Worker, Queue, Connection

from worker import test_run
#Configuration


app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['OUTPUT_FOLDER'] = './output'
app.config['SCRATCH_FOLDER'] = './scratch'

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)
q = Queue(connection=conn)

@app.route('/test_run_job', methods=['GET'])
def testrunjob():
    job = q.enqueue_call(
        func=test_run, args=(), result_ttl=5000
    )
    print(job.get_id())
    return job.get_id()


    
@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return str(job.result), 200
    else:
        return "Nay!", 202
    
@app.route('/run_job', methods=['POST'])
def runjob():
    if request.files:
        #attached_files_list = json.loads(request.args.get('filenames', '[]'))
        uploaded_file_mapping = {}
        
        print request.files.keys()
        
        for file_in_list in request.files.keys():
            file_request = request.files[file_in_list]
            
            if file_request:
                filename = id_generator(10)
                system_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_request.save(system_path)
                uploaded_file_mapping[file_in_list] = system_path
        
        print uploaded_file_mapping
        output_file = os.path.join(app.config['OUTPUT_FOLDER'], id_generator(10))
        scratch_folder = os.path.join(app.config['SCRATCH_FOLDER'], id_generator(10))
        make_sure_path_exists(scratch_folder)
        
        execute_job(uploaded_file_mapping, output_file, scratch_folder)
        
        return send_file(output_file, mimetype='image/gif')
    
    return "MING"

#Given the deposited data do something with it
def execute_job(input_files_path_map, output_file_path, scratch_path):
    cmd = "make_emperor.py " + " -i " + input_files_path_map["coordinate"] + " -m " + input_files_path_map["mapping"] + " -o " + scratch_path
    print cmd
    subprocess.call([cmd], shell=True)
    cp_cmd = "cp " + os.path.join(scratch_path, "index.html") + " " + output_file_path
    print cp_cmd
    subprocess.call([cp_cmd], shell=True)
    
    
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
    
def make_sure_path_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0')