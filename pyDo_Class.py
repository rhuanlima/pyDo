import datetime
import os
import sys
from peewee import *
from readchar import readchar
from collections import OrderedDict

db = SqliteDatabase('pyDo_database.db')

class ToDo(Model):
    task = CharField(max_length=255)
    timestamp = DateTimeField(default=datetime.datetime.now)
    done = BooleanField(default=False)
    protected = BooleanField(default=False)

    class Meta:
        database = db

def close():
    db.close()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def initialize():
    db.connect()
    db.create_tables([ToDo], safe=True)


def view_entries(index, entries, single_entry):
    clear()

    index = index % len(entries)  # determines which entry is selected for modification
    if single_entry:  # to see only 1 entry
        entries = [entries[index]]
        index = 0
    else:
        print('\npyDO :: To Do List')
        print('=' * 40)
    prev_timestamp = None

    for ind, entry in enumerate(entries):
        timestamp = entry.timestamp.strftime('%d/%B/%Y')

        if timestamp != prev_timestamp:  # same timestamps get printed only once
            print('\n')
            print(timestamp)
            # print('=' * len(timestamp))
            prev_timestamp = timestamp

        if ind == index:  # placing the selection tick
            tick = '-> '
        else:
            tick = '   '

        print('{}{}'.format(tick, entry.task), end='')
        if entry.done:
            print('\t(DONE)', end='')
        if entry.protected:
            print('\t*', end='')
        print('')

    return entries  # so that we can modify the given entry if needed


def add_entry(index, entries):
    '''Add a new task'''
    new_task = input('\nTo do: ')
    if input('Protect [yN]? ').lower().strip() == 'y':
        protect = True
    else:
        protect = False
    ToDo.create(task=new_task,
                protected=protect)


def cleanup_entries(index, entries):
    '''Cleanup: delete completed and unprotectedtask'''
    if (input('All of your completed and unprotected tasks will be deleted! Ok? [y/N]').lower().strip() == 'y'):
        now = datetime.datetime.now()
        for entry in entries:
            # if (now - entry.timestamp >= datetime.timedelta(1, 0, 0) and entry.done and not entry.protected):
            if (now - entry.timestamp >= datetime.timedelta(1, 0, 0) and entry.done and not entry.protected):
                entry.delete_instance()


def modify_task(index, entries):
    """Modify task"""
    entry = view_entries(index, entries, True)[0]
    new_task = input('> ')
    entry.task = new_task
    entry.save()


def delete_entry(index, entries):
    """Delete entry"""
    entry = view_entries(index, entries, True)[0]
    if (input('Are you sure [y/N]? ').lower().strip() == 'y'):
        entry.delete_instance()


def toggle_done(index, entries):
    """Toggle 'DONE'"""
    entry = view_entries(index, entries, True)[0]
    entry.done = not entry.done
    entry.save()


def toggle_lock(index, entries):
    """Toggle 'LOCK'"""
    entry = view_entries(index, entries, True)[0]
    entry.protected = not entry.protected
    entry.save()


def menu_loop():
    choice = None
    index = 0
    entries = ToDo.select().order_by(ToDo.timestamp.asc())
    while choice != 'q':
        if len(entries) != 0:
            view_entries(index, entries, False)
            print('\n' + '=' * 40 + '\n')
            print('Previous/Next: p/n \n')
        for key, value in main_menu.items():
            print('{}) {}'.format(key, value.__doc__))
        print('q) Quit')
        print('\nAction: ', end='')
        choice = readchar()

        if choice in main_menu:
            try:
                main_menu[choice](index, entries)
            except ZeroDivisionError:
                continue
            entries = ToDo.select().order_by(ToDo.timestamp.asc())  # update entries after operations

        elif choice == 'n':
            index += 1
        elif choice == 'p':
            index -= 1


main_menu = OrderedDict([
    ('a', add_entry),
    ('c', cleanup_entries),
    ('m', modify_task),
    ('d', toggle_done),
    ('l', toggle_lock),
    ('e', delete_entry)
])
