# RPCServer

This is a simple RPC webserver complete with a worker thread.

What this allows you to do is simply add a custom html form and the parameters that are created by the form are handed off to a worker thread and you can implement your own custom python function to do some processing and generate some result. This result is then handed back to the user as a zipped up file.

While this doesn't offer too much flexibility, it does make it easy to write really simple one off scripts for users to try out.

## Setting up Everything
* Clone repository
* Download redis server, build it
* Pip install flask, rq, rq-dashboard

## Customizing Your Job
* Edit templates/homepage.html to modify exactly the form parameters
* Edit worker.py, specifically the custom_worker_task function in order to do what you want. Just make sure you output what you want returned to the user in the output_folder. All form parameters, including paths to the input files are in the input_parameters dictionary.


## Starting everything
* Run Redis Servier
* Start python web server (python ./flask.py) which will be by default running at port 5000
* Start worker thread (python ./worker.py)
* Start rq-dashboard for more queue monitoring

### Caveats
* webserver and worker threads should be run from the same working directory
