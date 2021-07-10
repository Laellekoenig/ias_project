import pickle
import os
import sys
from logic.file_handler import DIR_BACNET, make_dirs

# determine absolute path of this folder
dirname = os.path.abspath(os.path.dirname(__file__))

# Import from gruppe04 (year 2020)
folderG4 = os.path.join(dirname, '../../dependencies/04-logMerge/eventCreationTool')
sys.path.append(folderG4)
import EventCreationTool

# import gruppe07 interface
folderG7 = os.path.join(dirname, '../../dependencies/07-14-logCtrl/src')
sys.path.append(folderG7)

from logStore.database.database_handler import DatabaseHandler
from logStore.transconn.database_connector import DatabaseConnector
#from testfixtures import LogCapture
from logStore.funcs.event import Event, Meta, Content
from logStore.appconn.chat_connection import ChatFunction
from feedCtrl.uiFunctionsHandler import UiFunctionHandler
from logStore.transconn.database_connector import DatabaseConnector

class BACCore:

    def __init__(self):
        self.pickle_file_names = ['personList.pkl', 'username.pkl']  # use to reset user or create new one
        self.switch = ["", "", ""]
        self.ufh = UiFunctionHandler()
    
    # return 1 if user already exists; 0 if not
    def exists_user(self):
        if not os.path.exists(DIR_BACNET + '/' + self.pickle_file_names[0]):
            pickle.dump(list(), open(DIR_BACNET + '/' + self.pickle_file_names[0], "wb"))  # create an empty object
        if not os.path.exists(DIR_BACNET + '/' + self.pickle_file_names[1]):
            self.create_user("test_user") # replace with interactive gui
            return 0
        return 1

    def create_user(self, user_name):
        make_dirs()
        if user_name != "" and len(user_name) <= 32:            
            ecf = EventCreationTool.EventFactory()
            public_key = ecf.get_feed_id()
            print(public_key)
            """
            chat_function = ChatFunction()
            first_event = ecf.first_event('chat', chat_function.get_host_master_id())
            
            chat_function.insert_event(first_event)
            """

            self.dictionary = {
                'user_name': user_name,
                'public_key': public_key
            }
            pickle.dump(self.dictionary, open(DIR_BACNET + '/' + self.pickle_file_names[1], "wb"))  # save user_name and key
            print("Your user_name has been saved:", user_name)

            return 1
        else:
            return 0
    
    def create_feed(self, feed_name):
        
        ecf = EventCreationTool.EventFactory()
        master_feed_id = self.ufh.get_host_master_id()
        dictionary = {
            'master_feed': master_feed_id
        }
        first_event = ecf.create_first_event('bac_news/MASTER', dictionary)
        print(first_event)
        

        
        list_of_feed_ids = EventCreationTool.EventCreationTool.get_stored_feed_ids()
        d = DatabaseConnector()
        for f in list_of_feed_ids:
            print(d.get_current_seq_no(f))
        #print(list_of_feed_ids)

    def create_event(self, feed_id):
        #first_event = EventCreationTool.EventFactory.
        dictionary = {
            'user_name': 'user1',
            'public_key': 'password'
        }
        new_event = ecf.next_event('bac_news/' + feed_name, dictionary)

        


