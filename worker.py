import os
import subprocess
import redis
from rq import Worker, Queue, Connection

listen = ['default']
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)

def test_run():
    print 'RUNNING JOB'
    return "MING"

    
#Test Execution of thing
def execute_qiime_pcoa(input_files_path_map, output_file_path, scratch_path):
    bucket_table_path = input_files_path_map["bucket_table"]
    metadata_file = input_files_path_map["mapping"]
    
    output_biom_file = os.path.join(scratch_path, "intermediate_bucket.biom")
    param_filename = os.path.join(scratch_path, "params.txt")
    metabolomic_table = os.path.join(scratch_path, "metabolomic_table.txt")
    scratch_bdiv = os.path.join(scratch_path, "bdiv")
    
    cmd_line = "biom convert -i " + bucket_table_path + " -o " + output_biom_file + " --table-type=\"Metabolite table\" --to-hdf5" 
    
    subprocess.call([cmd_line], shell=True)
    print cmd_line
    
    #cmd_line = "echo \"beta_diversity:metrics euclidean,pearson,gower,bray_curtis\" > " + param_filename
    cmd_line = "echo \"beta_diversity:metrics euclidean\" > " + param_filename
    subprocess.call([cmd_line], shell=True)
    print cmd_line
    
    cmd_line = "biom summarize-table -i " + output_biom_file + " -o " + metabolomic_table
    subprocess.call([cmd_line], shell=True)
    print cmd_line
    
    cmd_line = "beta_diversity_through_plots.py -i " + output_biom_file + " -o " + scratch_bdiv + " -p " + param_filename + " -m " + metadata_file +  " -e 30676"
    subprocess.call([cmd_line], shell=True)
    print cmd_line
    
    output_file_generated_html = os.path.join(scratch_bdiv, "euclidean_emperor_pcoa_plot/index.html")
    
    return open(output_file_generated_html, "r").read()
    
    
    
#Given the deposited data do something with it, Deprecated
def execute_job(input_files_path_map, output_file_path, scratch_path):
    cmd = "make_emperor.py " + " -i " + input_files_path_map["coordinate"] + " -m " + input_files_path_map["mapping"] + " -o " + scratch_path
    print cmd
    subprocess.call([cmd], shell=True)
    cp_cmd = "cp " + os.path.join(scratch_path, "index.html") + " " + output_file_path
    print cp_cmd
    subprocess.call([cp_cmd], shell=True)
    
    
if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()