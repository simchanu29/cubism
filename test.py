import os
import subprocess
root = os.path.realpath(__file__)[:-len('test.py')]+"/tasks"
print os.listdir(root)

subprocess.call('tasks/task_example/do.sh', shell=True)
