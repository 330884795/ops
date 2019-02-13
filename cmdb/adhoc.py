import os
import time
import datetime
from pymongo import MongoClient
import json
import shutil
from ansible.parsing.dataloader import DataLoader
from collections import namedtuple
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import ansible.constants as C


mongoinfo = {"host":"10.25.233.225","port":"27017","user":"ansible","password":"ansible","dbname":"ansible"}
TIME_FORMAT='%Y-%m-%d %H:%M:%S'

def InsertDB(values):
    global mongoinfo
    dbhost = mongoinfo['host']
    dbport = mongoinfo['port']
    dbuser = mongoinfo['user']
    dbpwd  = mongoinfo['password']
    dbname = mongoinfo['dbname']
    uri = 'mongodb://%s:%s@%s/%s'%(dbuser,dbpwd,dbhost,dbname)
    client = MongoClient(uri)
    db = client.ansible
    db.new.insert_one(values)


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
        InsertDB(result)

    def runner_on_ok(self, host, res):
        now = datetime.datetime.now()
        result = res
        result['time'] = now.strftime(TIME_FORMAT)
        result['status'] = 'ok'
        result['ip'] = host
        InsertDB(result)

    def runner_on_unreachable(self, host, res):
        now = datetime.datetime.now()
        result = res
        result['time'] = now.strftime(TIME_FORMAT)
        result['status'] = 'unreachable'
        result['ip'] = host
        InsertDB(result)

    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        # InsertDB(dict({"task_name":host}))
        self.runner_on_ok(host, result._result)


Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff'])
# initialize needed objects
loader = DataLoader()
options = Options(connection='ssh', module_path=['/root/anaconda3/lib/python3.6/site-packages/ansible/modules'], forks=10, become=None, become_method=None, become_user=None, check=False,diff=False)
passwords = dict(vault_pass='secret')

# Instantiate our ResultCallback for handling results as they come in
results_callback = ResultCallback()

# create inventory and pass to var manager
# use path to host config file as source or hosts in a comma separated string


# create play with tasks
def tasks(host,command):
    inventory = InventoryManager(loader=loader, sources=['/etc/ansible/'+host+'-hosts'])
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    play_source =  dict(
        name = "Ansible Play",
        hosts = 'all',
        gather_facts = 'no',
        tasks = [
            dict(action=dict(module='shell', args=command)),
         ]
    )
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # actually run it
    tqm = None
    try:
        tqm = TaskQueueManager(
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              options=options,
              passwords=passwords,
              stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin
          )
        result = tqm.run(play)
    finally:
        if tqm is not None:
            tqm.cleanup()
