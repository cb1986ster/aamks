#!/usr/bin/python3
import os
import sys
sys.path.append(os.environ['AAMKS_PATH'])
from include import Json
from include import SendMessage
import json
from collections import OrderedDict
from subprocess import Popen,PIPE
import zipfile
import traceback

try:
    class WorkerReport():
        def __init__(self, sim_id, project, animation_data, psql_data): # {{{
            ''' 
            Runs on a worker. Write /home/aamks/project/sim_id.json on each aRun
            completion. Then inform gearman server to scp to itself
            /home/aamks/project/sim_id.json via aOut service. Gearman server will
            process this json via /usr/local/aamks/manager/results_collector.py.
            Gearman server will psql insert and will scp the worker's animation to
            itself. 
            '''

            self.project_dir="/home/aamks/{}".format(project)
            try:
                os.makedirs(self.project_dir, exist_ok=True)
            except:
                pass
            self.sim_id=sim_id
            self._write_report(psql_data)
            self._write_animation(animation_data)
        # }}}
        def _write_report(self, psql_data):# {{{
            j=Json()
            host=os.uname()[1]
            report=OrderedDict()
            report['worker']=host
            report['sim_id']=self.sim_id 
            report['animation']="{}/{}.anim.zip".format(self.project_dir, self.sim_id)
            report['psql']=psql_data
            json_file="{}/report_{}.json".format(self.project_dir, self.sim_id)
            j.write(report, json_file)
            Popen("gearman -h {} -f aOut '{} {} {}'".format(os.environ['AAMKS_SERVER'], host, json_file, self.sim_id), shell=True)
        # }}}
        def _write_animation(self, animation_data):# {{{
            zf = zipfile.ZipFile("{}/{}.anim.zip".format(self.project_dir, self.sim_id), mode='w', compression=zipfile.ZIP_DEFLATED)
            try:
                zf.writestr("anim.json", json.dumps(animation_data))
            finally:
                zf.close()
        # }}}
    def example_animation_data(sim_id):# {{{
        ''' TODO: temporary. Should come as argument in the future '''
        animation_data=dict()
        animation_data['data']=[
                [ [ 1000 , 1150 , 20  , 200  , "N" , 1 ] , [ 1000 , 1150 , 200 , 0   , "N" , 1 ] ] ,
                [ [ 1100 , 1850 , 200 , -300 , "N" , 1 ] , [ 1500 , 1150 , 200 , 0   , "N" , 1 ] ] ,
                [ [ 1500 , 1150 , 200 , 80   , "N" , 0 ] , [ 5000 , 1150 , 200 , 0   , "N" , 1 ] ] ,
                [ [ 5000 , 1850 , 200 , -200 , "N" , 0 ] , [ 6000 , 1150 , 200 , 0   , "N" , 1 ] ] ,
                [ [ 6000 , 1150 , 200 , 200  , "N" , 0 ] , [ 0    , 0    , 200 , 200 , "N" , 0 ] ] ,
                [ [ 0    , 0    , 200 , 200  , "N" , 0 ] , [ 0    , 0    , 200 , 200 , "N" , 0 ] ] 
            ]            
        animation_data['frame_rate']=2
        animation_data['project_name']=project
        animation_data['simulation_id']=sim_id
        animation_data['simulation_time']=200
        animation_data['time_shift']=150.61 
        return animation_data
# }}}

    sim_id=os.path.basename(sys.argv[1])
    project=sys.argv[2]
    try:
        sim_id=os.path.basename(sys.argv[1])
        project=sys.argv[2]
        animation_data=sys.argv[3]
        psql_data=sys.argv[4]
    except:
        ''' Testing without gearman. '''  
        sim_id="1"
        project="simple"
        animation_data=example_animation_data(sim_id)
        psql_data="psql report"

    report=WorkerReport(sim_id, project, animation_data, psql_data)

except:
    t=traceback.format_exc()
    with open("/tmp/aamks_fail.log", "w") as f: 
        f.write(t)
    SendMessage('err')
    raise Exception("worker fail")
