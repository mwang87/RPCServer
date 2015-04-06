
import os
from flask import Flask, request, redirect, url_for, send_file

import random
import string
import json


import redis
from rq import Worker, Queue, Connection
from rq.job import Job

from worker import test_run
from worker import execute_qiime_pcoa
#Configuration


app = Flask(__name__, static_folder='./static', static_url_path='/results')
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
        func=test_run, args=(), result_ttl=86000
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
        
        print "SCRATCH : " + scratch_folder
        job = q.enqueue_call(
            func=execute_qiime_pcoa, args=(uploaded_file_mapping, output_file, scratch_folder), result_ttl=86000
        )
        print(job.get_id())
        return job.get_id()
        
        #execute_job(uploaded_file_mapping, output_file, scratch_folder)
        
        #return send_file(output_file, mimetype='image/gif')
    
    return "ERROR", 400


    
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
    
def make_sure_path_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0')
