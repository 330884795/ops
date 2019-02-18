
import os
import time
import datetime
from pymongo import MongoClient
import json
import shutil
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
import ansible.constants as C
import ansible.executor.task_result


mongoinfo = {"host":"dds-bp11e38d33b092a41.mongodb.rds.aliyuncs.com","port":"3717","user":"ansible","password":"ansible","dbname":"ansible"}
TIME_FORMAT='%Y-%m-%d %H:%M:%S'

def InsertDB(values):
    global mongoinfo
    dbhost = mongoinfo['host']
    dbport = mongoinfo['port']
    dbuser = mongoinfo['user']
    dbpwd  = mongoinfo['password']
    dbname = mongoinfo['dbname']
    uri = 'mongodb://%s:%s@%s:%s/%s' % (dbuser, dbpwd, dbhost, dbport, dbname)
    client = MongoClient(uri)
    db = client.ansible
    db.newplaybook.insert(values)


class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """

    def runner_on_failed(self, host, res, ignore_errors=False):
        now = datetime.datetime.now()
        result = res
        result['time'] = now.strftime(TIME_FORMAT)
        result['status'] = 'fail'
        result['ip'] = host
        #a = {'ip': host, 'err': result['stderr_lines'], 'succ_info': result['stdout_lines'],
        #     'status': result['status'], 'time': result['time'],
        #     'cmd': result['invocation']['module_args']['_raw_params']}
        InsertDB(result)

    def runner_on_ok(self, host, res):
        now = datetime.datetime.now()
        result = res
        result['time'] = now.strftime(TIME_FORMAT)
        result['status'] = 'ok'
        result['ip'] = host
        #a = {'ip': host, 'err': result['stderr_lines'], 'succ_info': result['stdout_lines'],
        #     'status': result['status'], 'time': result['time'],
        #     'cmd': result['invocation']['module_args']['_raw_params']}
        InsertDB(result)

    def runner_on_unreachable(self, host, res):
        now = datetime.datetime.now()
        result = res
        result['time'] = now.strftime(TIME_FORMAT)
        result['status'] = 'unreachable'
        result['ip'] = host
        #a = {'ip': host,  'succ_info': result['stdout_lines'],
        #     'status': result['status'], 'time': result['time'],
        #     'cmd': result['invocation']['module_args']['_raw_params']}
        InsertDB(result)

#    def v2_runner_on_ok(self, result):
#        host = result._host.get_name()
#        # InsertDB(dict({"task_name":host}))
#        self.runner_on_ok(host, result._result)




Options = namedtuple('Options',['connection','gather_facts','remote_user','ask_sudo_pass','verbosity','ack_pass','module_path', 'forks', 'become', 'become_method','become_user','check', 'listhosts', 'listtasks', 'listtags','syntax','sudo_user', 'sudo', 'diff'] )
# initialize needed objects
loader = DataLoader()
options = Options(connection='ssh',gather_facts='no',remote_user='root',ack_pass=None,sudo_user='root',forks=5, sudo='yes', ask_sudo_pass=False, verbosity=5,module_path=['/root/anaconda3/lib/python3.6/site-packages/ansible/modules'],become=True, become_method='sudo', become_user='root',check=None, listhosts=False,listtasks=False, listtags=None, syntax=None,diff=False)
passwords = dict(vault_pass='secret')

# Instantiate our ResultCallback for handling results as they come in
results_callback = ResultCallback()

# create inventory and pass to var manager
# use path to host config file as source or hosts in a comma separated string

#variable_manager.extra_vars = {'host':'e01'}


def tasksbook(file,hosts):
    inventory = InventoryManager(loader=loader, sources=hosts)
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    playbook = PlaybookExecutor(
              playbooks=[file],
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              options=options,
              passwords=passwords,
          )
    playbook._tqm._stdout_callback = results_callback
    playbook.run()
