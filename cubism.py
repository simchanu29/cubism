#!/usr/bin/python
# Author : Simon CHANU
# python2 and python3 compatible

"""
   Copyright 2018 Simon CHANU

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import sys, os
import curses
import ctypes
import urllib2
import time
import subprocess
import sys
import yaml

configPath = None

def check_is_admin():
    is_admin = (os.getuid() == 0)
    str_is_admin = "not"

    # print("Script {} connected to internet".format(str_is_admin)
    return (os.getuid() == 0)


def check_has_internet():
    try:
        response=urllib2.urlopen('http://www.google.com',timeout=20)
        return True
    except urllib2.URLError as err: pass
    return False

class Task:
    def __init__(self, name, path, win):
        self.win = win
        self.priority = 0
        self.name = name
        self.path = path
        self.dic = {
            'do':{'mode':0, 'todo':False, 'ask':True},
            'undo':{'mode':0, 'todo':False, 'ask':True},
            'check':{'mode':0, 'todo':False, 'ask':True}
        }

    def get_state(self, name):
        return self.dic[name]['todo']

    def get_asked(self, name):
        return self.dic[name]['ask']

    def cycle(self, name):
        self.dic[name]['mode'] = (self.dic[name]['mode'] + 1) % 3
        self.dic[name]['todo'] = (self.dic[name]['mode'] > 0)
        self.dic[name]['ask'] = (self.dic[name]['mode'] == 1)
        # h, w = self.win.getmaxyx()
        # self.win.addstr(0,0,str(self.dic[name]['mode'])[:w-1])
        # 0, F, F
        # 1, T, T
        # 2, T, F

    def execute(self, name):
        if name == 'do':
            return self.do()
        if name == 'undo':
            return self.undo()
        if name == 'check':
            return self.check()

    def do(self):
        curses.reset_shell_mode()
        subprocess.call(self.path+'/do.sh', shell=True)

        str_end = '[INSTALLER] Task '+str(self.name)+' finished, press key to continue'
        print('_'*len(str_end)+'\n')
        print(str_end)

        curses.reset_prog_mode()

    def undo(self):
        pass

    def check(self):
        pass

class Installer:
    def __init__(self, win, configPath=None):
        self.tasks = {}
        self.max_priority = 0
        self.tasks_root = os.path.realpath(__file__)[:-len("cubism.py")]+"/tasks"
        self.config = None

        # import config
        if configPath is not None:
            try:
                stream = open(configPath, 'r')
                self.config = yaml.load(stream)
                stream.close()
            except (yaml.YAMLError, IOError) as e:
                self.config = None
                stream.close()
                pass

        # import task list
        self.import_task_list(win)

    def get_tasks_from_priority(self, priority):
        dic_tasks = {}
        for task in self.tasks:
            task_obj = self.tasks[task]
            if task_obj.priority == priority:
                dic_tasks[task] = task_obj

        return dic_tasks

    def inc_task_priority(self, taskname):
        self.set_task_priority(taskname, self.tasks[taskname].priority + 1)

    def dec_task_priority(self, taskname):
        self.set_task_priority(taskname, max(self.tasks[taskname].priority - 1, 0))

    def set_task_priority(self, taskname, priority):
        # set priority
        self.tasks[taskname].priority = priority

        # update maximum priority
        max_priority = 0
        for task in self.tasks:
            max_priority = max(max_priority, self.tasks[task].priority)
        self.max_priority = max_priority

    def import_task_list(self, win):
        task_list = os.listdir(self.tasks_root)
        for task in task_list:
            self.tasks[task] = Task(task, self.tasks_root+"/"+task, win)
            if self.config is not None:
                if (task in self.config):
                    for function in ['do', 'undo', 'check']:
                        if (function in self.config[task]):
                            for attr in ['mode', 'todo', 'aks']:
                                if (attr in self.config[task][function]):
                                    self.tasks[task].dic[function][attr] = self.config[task][function][attr]


class Window:
    def __init__(self, height, width, begin_y, begin_x, name="anonymous"):
        self.win = curses.newwin(height, width, begin_y, begin_x)

        self.name = name
        self.x = begin_x
        self.y = begin_y
        self.height, self.width = self.win.getmaxyx()
        self.center_y = int((self.height // 2) - 2)
        self.center_x = int((self.width // 2) - 2)

    def update(self, height, width, new_y, new_x):
        pass
        self.x = new_x
        self.y = new_y
        self.height = height
        self.width = width
        self.center_y = int((self.height // 2) - 2)
        self.center_x = int((self.width // 2) - 2)
        self.win.resize(self.height, self.width)

        try:
            self.win.mvwin(self.y, self.x)
        except Exception:
            print("Valeurs x et y : {}, {}".format(self.y, self.x))
            print("Valeurs w et h : {}, {}".format(self.width, self.height))

            k = self.win.getch()
            while (k != ord('q')):
                time.sleep(0.2)
                k = self.win.getch()
            raise Exception


class Gui:

    def __init__(self, stdscr):
        self.k = 0
        self.cursor_x = 0
        self.cursor_y = 0
        self.height = 0
        self.width = 0
        self.center_y = 0
        self.center_x = 0
        self.stdscr = stdscr
        self.connectivity = False
        self.admin_rights = False
        self.tasktitle = "Idle"

        self.list_cursor_y = 0
        self.list_cursor_x = 0

        self.menu = 'Start Menu'
        self.highlighted_choice = 'None'
        self.request = None

        # set up timeout
        self.stdscr.timeout(200)

        # Clear and refresh the screen for a blank canvas
        self.stdscr.clear()
        self.stdscr.refresh()

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        self.height, self.width = self.stdscr.getmaxyx()
        self.center_y = int((self.height // 2) - 2)
        self.center_x = int((self.height // 2) - 2)

        begin_x = 0
        begin_y = 0
        height = 3
        width = self.width - 1
        self.header = Window(height, width, begin_y, begin_x, name="header")

        begin_x = 0
        begin_y = 3
        height = self.height - 4
        width = self.width
        self.body = Window(height, width, begin_y, begin_x, name="body")

        begin_x = 0
        begin_y = self.height - 1
        height = 1
        width = self.width
        self.footer = Window(height, width, begin_y, begin_x, name="footer")

        self.installer = Installer(self.body.win, configPath)
        self.run()

    def run(self):
        self.startcheck_menu()

        # Loop where k is the last character pressed
        while (self.k != ord('q')):

            # Initialization
            self.update_windows_size()

            if self.menu == 'Start Menu':
                self.start_menu()
            elif self.menu == 'Install Menu':
                self.request_menu('do')
            elif self.menu == 'Uninstall Menu':
                self.request_menu('undo')
            elif self.menu == 'Check Install Menu':
                self.request_menu('check')
            elif self.menu == 'Response Menu':
                self.response_menu(self.request)

            # Wait for next input
            self.k = self.stdscr.getch()

    def update_windows_size(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.center_y = int((self.height // 2) - 2)
        self.center_x = int((self.width // 2) - 2)

        self.header.update(3, self.width, 0, 0)
        self.body.update(self.height - 4, self.width, 3, 0)
        self.footer.update(1, self.width, self.height - 1, 0)

    def draw_statusbar(self, win):
        # Declaration of strings
        statusbar_info = "Exit: press 'q' | Internet: {} | Admin: {} | Info: {}".format(self.connectivity, self.admin_rights, self.tasktitle)
        statusbar_blank = " " * (win.width - len(statusbar_info) - 1)
        statusbar_str = (statusbar_info + statusbar_blank)[:(win.width - 1)]

        # Render status bar
        win.win.attron(curses.color_pair(3))
        win.win.addstr(max(0, win.height-1), 0, statusbar_str)
        win.win.attroff(curses.color_pair(3))

    def draw_startmenu(self, win):
        # Declaration of strings
        title = "CuBISM"[:win.width-1]
        subtitle = "Curses Bash Install Scripts Manager"[:win.width-1]

        # Centering calculations
        start_x_title = int((win.width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((win.width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)

        # Turning on attributes for title
        win.win.attron(curses.color_pair(2))
        win.win.attron(curses.A_BOLD)

        # Rendering title
        win.win.addstr(0, start_x_title, title)

        # Turning off attributes for title
        win.win.attroff(curses.color_pair(2))
        win.win.attroff(curses.A_BOLD)

        # print(rest of text
        win.win.addstr(1, start_x_subtitle, subtitle)
        win.win.addstr(2, (win.width // 2) - 2, '-' * 4)

    def draw_listmenu(self, win):

        # Declaration of strings
        install = "Install Menu"
        uninstall = "Uninstall Menu"
        check = "Check Install Menu"
        list_menu = [install, uninstall, check]
        list_dic = {
            install: (3, win.center_x - 3 - 4),
            uninstall: (5, win.center_x - 4 - 4),
            check: (7, win.center_x - 5 - 4)
        }

        win.win.border()

        # Cursor handler
        if self.k == curses.KEY_DOWN:
            self.list_cursor_y = min(len(list_menu) - 1 , self.list_cursor_y + 1)
        elif self.k == curses.KEY_UP:
            self.list_cursor_y = max(0, self.list_cursor_y - 1)
        elif self.k == 10:
            self.menu = self.highlighted_choice
        self.highlighted_choice = list_menu[self.list_cursor_y]

        # Render start menu
        for choice in list_menu:
            if self.highlighted_choice is choice:
                win.win.attron(curses.color_pair(3))
            menu_str = ("- " + choice + " -")[:win.width - 1]
            win.win.addstr(list_dic[choice][0], list_dic[choice][1], menu_str)
            if self.highlighted_choice is choice:
                win.win.attroff(curses.color_pair(3))

        # Render help
        win.win.attron(curses.color_pair(1))
        height = win.height - 2
        x_offset = 22
        win.win.addstr(height - 3, win.center_x - x_offset, (" _____________________________________________" )[:win.width-1])
        win.win.addstr(height - 2, win.center_x - x_offset, ("| To import a config file, add its path as an |")[:win.width-1])
        win.win.addstr(height - 1, win.center_x - x_offset, ("| argument to CuBISM                          |")[:win.width-1])
        win.win.addstr(height, win.center_x - x_offset,     ("|_____________________________________________|")[:win.width-1])
        win.win.attroff(curses.color_pair(1))

    def draw_responsemenu(self, win):
        # Ce sont les taches qui vont remplir ce menu
        win.win.border()
        self.cursor_x = 0
        self.cursor_y = 0
        win.win.move(self.cursor_x, self.cursor_y)

    def draw_requestmenu(self, win):
        list_menu = ['main menu', 'execute']

        win.win.border()

        # Safety for first call
        if self.highlighted_choice not in self.installer.tasks:
            if self.highlighted_choice not in list_menu:
                self.highlighted_choice = list(self.installer.tasks)[0]

        # Cursor handler
        if self.k == curses.KEY_DOWN:
            self.list_cursor_y = min(len(self.installer.tasks) + len(list_menu) - 1 , self.list_cursor_y + 1)
        elif self.k == curses.KEY_UP:
            self.list_cursor_y = max(0, self.list_cursor_y - 1)
        elif self.k == curses.KEY_RIGHT:
            self.installer.inc_task_priority(self.highlighted_choice)
        elif self.k == curses.KEY_LEFT:
            self.installer.dec_task_priority(self.highlighted_choice)
        elif self.k == 10:
            if self.highlighted_choice == list_menu[1]:
                self.menu = 'Response Menu'  # Execution de la requete
            elif self.highlighted_choice == list_menu[0]:
                self.menu = 'Start Menu'  # Retour en arriere
            else:
                self.installer.tasks[self.highlighted_choice].cycle(self.request)

        # Ajoute les fonctions de cancel et execute apres la liste des taches
        if self.list_cursor_y < len(self.installer.tasks):
            self.highlighted_choice = list(self.installer.tasks)[self.list_cursor_y]
        else:
            self.highlighted_choice = list_menu[self.list_cursor_y - len(self.installer.tasks)]

        # Render tasks
        for idx, val in enumerate(self.installer.tasks):
            task = self.installer.tasks[val]
            check = " "
            if task.get_state(self.request):
                if task.get_asked(self.request):
                    check = "x"
                else:
                    check = "o"

            if self.highlighted_choice is task.name:
                win.win.attron(curses.color_pair(3))
            task_str = "[{}] - [{}] - {}".format(task.priority, check, task.name)[:win.width - 1]
            win.win.addstr(idx + 2, 2, task_str)
            if self.highlighted_choice is task.name:
                win.win.attroff(curses.color_pair(3))

        # Render cancel
        if self.highlighted_choice is list_menu[0]:
            win.win.attron(curses.color_pair(3))
        win.win.addstr(win.height - 3, win.center_x - 15, list_menu[0][:win.width - 1])
        if self.highlighted_choice is list_menu[0]:
            win.win.attroff(curses.color_pair(3))

        # Render execute
        if self.highlighted_choice is list_menu[1]:
            win.win.attron(curses.color_pair(3))
        win.win.addstr(win.height - 3, win.center_x + 15, list_menu[1][:win.width - 1])
        if self.highlighted_choice is list_menu[1]:
            win.win.attroff(curses.color_pair(3))

        # Render helptext

        win.win.attron(curses.color_pair(1))
        help_width = 39
        win.win.addstr(1, win.width - help_width,  (" __________________________________")[:win.width-1])
        win.win.addstr(2, win.width - help_width,  ("| Help                             |")[:win.width-1])
        win.win.addstr(3, win.width - help_width,  ("|                                  |")[:win.width-1])
        win.win.addstr(4, win.width - help_width,  ("| ENTER : cycle mode on task       |")[:win.width-1])
        win.win.addstr(6, win.width - help_width,  ("| [x] : will be executed with user |")[:win.width-1])
        win.win.addstr(5, win.width - help_width,  ("| [ ] : won't be executed          |")[:win.width-1])
        win.win.addstr(7, win.width - help_width,  ("|       prompt at the end          |")[:win.width-1])
        win.win.addstr(8, win.width - help_width,  ("| [o] : will be executed without   |")[:win.width-1])
        win.win.addstr(9, win.width - help_width,  ("|       user prompt at the end     |")[:win.width-1])
        win.win.addstr(10, win.width - help_width, ("| Tasks will be executed in a      |")[:win.width-1])
        win.win.addstr(11, win.width - help_width, ("| decreasing priority order        |")[:win.width-1])
        win.win.addstr(12, win.width - help_width, ("| The highest the priority is, the |")[:win.width-1])
        win.win.addstr(13, win.width - help_width, ("| soonest it is executed           |")[:win.width-1])
        win.win.addstr(14, win.width - help_width, ("|__________________________________|")[:win.width-1])
        win.win.attroff(curses.color_pair(1))

    def draw(self, screen, *args):
        screen.win.clear()

        for function in args:
            function(screen)

        screen.win.refresh()

    def startcheck_menu(self):

        # Step 1 connectivity
        self.tasktitle = "check internet"
        self.draw(self.header, self.draw_startmenu)
        self.draw(self.footer, self.draw_statusbar)

        self.connectivity = check_has_internet()

        # Step 2 last update
        self.tasktitle = "check admin rights"
        self.draw(self.footer, self.draw_statusbar)

        self.admin_rights = check_is_admin()

        # Step 3 last update
        self.tasktitle = "Idle"
        self.draw(self.footer, self.draw_statusbar)

        # Allow user to see admin check
        # time.sleep(0.2)

    def start_menu(self):
        self.tasktitle = "Start Menu"

        if self.k == curses.KEY_RESIZE:
            self.draw(self.header, self.draw_startmenu)
        self.draw(self.body, self.draw_listmenu)
        self.draw(self.footer, self.draw_statusbar)

        # Reset if exiting out of Start Menu
        if self.menu != 'Start Menu':
            self.list_cursor_y = 0

    def request_menu(self, request):
        self.request = request
        self.tasktitle = request

        if self.k == curses.KEY_RESIZE:
            self.draw(self.header, self.draw_startmenu)
        self.draw(self.body, self.draw_requestmenu)
        self.draw(self.footer, self.draw_statusbar)

        # Reset if exiting to Start Menu
        if self.menu == 'Start Menu':
            self.list_cursor_y = 0

    def response_menu(self, request):
        self.stdscr.timeout(-1)

        for prio in range(self.installer.max_priority+1):
            tasks_to_do = self.installer.get_tasks_from_priority(prio)
            for task in tasks_to_do:
                if self.installer.tasks[task].get_state(self.request):

                    self.tasktitle = task
                    self.installer.tasks[task].execute(self.request)

                    if self.installer.tasks[task].get_asked(self.request):
                        self.stdscr.getch()

        # Reset if exiting to Start Menu
        self.menu = 'Start Menu'
        self.tasktitle = 'Finished, press key'
        self.list_cursor_y = 0

        self.draw(self.footer, self.draw_statusbar)
        self.stdscr.getch()

        self.stdscr.timeout(200)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        configPath = sys.argv[1]
    curses.wrapper(Gui)
