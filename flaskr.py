
import os
from flask import Flask, request, redirect, url_for, send_file, render_template

import random
import string
import json


import redis
from rq import Worker, Queue, Connection
from rq.job import Job

from worker import execute_worker_task
#Configuration


app = Flask(__name__, static_folder='./static/result_output', static_url_path='/result_output')
app.debug = True
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['OUTPUT_FOLDER'] = './output'
app.config['SCRATCH_FOLDER'] = './scratch'
app.config['ZIPPED_RESULTS'] = './static/result_output'

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)
q = Queue(connection=conn)

@app.route('/', methods=['GET'])
def renderhomepage():
    return render_template('homepage.html')

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

    zipped_filepath = "/result_output/" + job.get_id() + ".tar.gz"
    print zipped_filepath

    if job.is_finished:
        result_return = str(job.result)
        return render_template("results_page.html", zipped_filepath=zipped_filepath, result_return=result_return)
        #return str(job.result), 200

    else:
        return render_template("refresh_page.html")
    
@app.route('/run_job', methods=['POST'])
def runjob():
    job_parameters = {}

    #Finding all Parameters
    print request.form
    for key in request.form:
        print key
        print request.form[key]
        job_parameters[key] = request.form[key]


    #saving files in a location and then saving into a full parameters map
    print request.files

    job_id = id_generator(10)

    #Saving Files
    if request.files:
        
        print request.files.keys()
        
        for file_in_list in request.files.keys():
            file_request = request.files[file_in_list]
            
            if file_request:
                filename = job_id
                system_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_request.save(system_path)
                job_parameters[file_in_list] = system_path


    output_folder = os.path.join(app.config['OUTPUT_FOLDER'], job_id)
    scratch_folder = os.path.join(app.config['SCRATCH_FOLDER'], job_id)
    zipped_result = os.path.join(app.config['ZIPPED_RESULTS'], job_id + ".tar.gz")

    make_sure_path_exists(output_folder)
    make_sure_path_exists(scratch_folder)

    job = q.enqueue_call(
        func=execute_worker_task, args=(job_parameters, output_folder, scratch_folder, zipped_result), result_ttl=86000, timeout=3600, job_id=job_id
    )

    print "Job ID: " + job_id

    return redirect("/results/" + job_id)


    
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
    
def make_sure_path_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0')
