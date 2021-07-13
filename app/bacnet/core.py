import pickle
import os
import sys
from datetime import datetime
from logic.file_handler import DIR_BACNET, make_dirs
from pathlib import Path

import json

# determine absolute path of this folder
dirname = os.path.abspath(os.path.dirname(__file__))

"""
# Import from gruppe04 (year 2020)
folderG4 = os.path.join(dirname, '../../dependencies/04-logMerge/eventCreationTool')
sys.path.append(folderG4)
import EventCreationTool
"""

# import gruppe07 interface
folderG7 = os.path.join(dirname, '../../dependencies/07-14-logCtrl/src')
sys.path.append(folderG7)

from logStore.database.database_handler import DatabaseHandler
from logStore.transconn.database_connector import DatabaseConnector
#from testfixtures import LogCapture
from logStore.funcs.event import Event, Meta, Content
from logStore.funcs.EventCreationTool import EventCreationTool, EventFactory
from logStore.appconn.chat_connection import ChatFunction
from logStore.appconn.feed_ctrl_connection import FeedCtrlConnection
from feedCtrl.uiFunctionsHandler import UiFunctionHandler
from logStore.transconn.database_connector import DatabaseConnector
from feedCtrl.eventCreationWrapper import EventCreationWrapper

folderG7 = os.path.join(dirname, '../../dependencies/04-logMerge/logMerge')
sys.path.append(folderG7)
from LogMerge import LogMerge

class BACCore:

    def __init__(self):
        self.pickle_file_names = ['personList.pkl', 'username.pkl']  # use to reset user or create new one
        self.switch = ["", "", ""]
        #self.ufh = UiFunctionHandler()
        #self.db_connector = DatabaseConnector()
        #self.setup_db()
    
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
    
    def create_feed(self, article_list_name):
        #print(d.get_all_feed_ids())
        #print(d.get_master_feed_id())
        """
        ecf = EventFactory()
        first_event = ecf.next_event('bac_news', self.master_feed_id)
        """
        fcc = FeedCtrlConnection()
        
        ect = EventCreationTool()
        public_key = ect.generate_feed()
        first_event = ect.create_first_event(public_key, 'bac_news/new_article', {'master_feed': self.master_feed_id})
        

        event = self.db_connector.get_current_event(self.master_feed_id)
        ecf_master = EventFactory(event)
        eventCreationWrapper = EventCreationWrapper(ecf_master)

        new_feed_event = eventCreationWrapper.create_newFeed(public_key, 'bac_news')
        fcc.add_event(new_feed_event)
        fcc.add_event(first_event)

        # create event containing list name, host name and creation date
        ect = EventCreationTool()
        dictionary = {  'host' : self.get_event_content(self.master_feed_id, 2)[1]['name'],
                        'list_name' : article_list_name,
                        'date' : datetime.now().isoformat() }
        second_event = ect.create_event_from_previous(first_event, 'bac_news/new_article', dictionary)
        fcc.add_event(second_event)
        """
                dictionary = {
                    'user_name': 'user1',
                    'public_key': 'password'
                }
                new_event = ecf.next_event('bac_news/' + feed_name, dictionary)
                dictionary2 = {
                    'user_name': 'user2',
                    'public_key': 'password2'
                }
                new_event = ecf.next_event('bac_news/' + feed_name, dictionary2)
                dictionary3 = {
                    'user_name': 'user3',
                    'public_key': 'password3'
                }
                new_event = ecf.next_event('bac_news/' + feed_name, dictionary3)
                #print(first_event)
                
                list_of_feed_ids = EventCreationTool.EventCreationTool.get_stored_feed_ids()
                print(list_of_feed_ids)
                
                for seq in range(0, 2):
                    pass
                    #print(d.get_event(list_of_feed_ids[1], seq))
                #print(list_of_feed_ids)
        """

        # Creates an event for the Feed given by the feed_id with the content found in the .json article file
        # returns 0, if there was an error, return 1 if event successfully created and added to feed.
    def create_event(self, feed_id, article_name):
        #first_event = EventCreationTool.EventFactory.
        #print(feed_ids)
        #event = self.db_connector.get_current_event(self.db_connector.get_all_feed_ids()[2])
        event = self.db_connector.get_current_event(feed_id)
        #print(event)

        try:
            f = open(str(Path.home()) + '/BACNews/Articles/' + article_name + ".json", "r")
            data = f.read()
            f.close()

            """dictionary = {
                'user_name': 'user1',
                'public_key': 'password'
            }"""
            
            ect = EventCreationTool()
            new_event = ect.create_event_from_previous(event, 'bac_news/new_article', data)
            fcc = FeedCtrlConnection()
            fcc.add_event(new_event)
            return 1
        except:
            return 0


    def get_event_content(self, feed_id, seq_no):
        cbor_event = self.db_connector.get_event(feed_id, seq_no)
        event = Event.from_cbor(cbor_event)
        return event.content.content
    
        #print(list_of_feed_ids[5])
        #print(d.get_current_event(list_of_feed_ids[1]))
    def exists_db(self):
        self._fcc = FeedCtrlConnection()
        lastEvent = self._fcc.get_my_last_event()
        if lastEvent is not None:
            return 1
        return 0

    def setup_db(self, user_name=''):
        # try catch or if None??
        lastEvent = self._fcc.get_my_last_event()
        if lastEvent is not None:
            self.master_feed_id = self._fcc.get_host_master_id()
            self.db_connector = DatabaseConnector()
            self.user_name = self.get_user_name()
        else:
            self._ecf = EventFactory()
            self._eventCreationWrapper = EventCreationWrapper(self._ecf)
            _firstEvent = self._eventCreationWrapper.create_MASTER()
            _secondEvent = self._eventCreationWrapper.create_radius(1)
            _thirdEvent = self._eventCreationWrapper.create_name(user_name)
            self._fcc.add_event(_firstEvent)
            self._fcc.add_event(_secondEvent)
            self._fcc.add_event(_thirdEvent)
            self.master_feed_id = self._fcc.get_host_master_id()
            self.db_connector = DatabaseConnector()
            self.user_name = user_name

    def get_user_name(self):
        print(self.get_event_content(self.master_feed_id, 2)[1]["name"])
        return(self.get_event_content(self.master_feed_id, 2)[1]["name"])

    def get_feednames_from_host(self):
        feed_names = list()
        feed_ids = self.get_all_feed_ids()
        print(feed_ids)
        for feed_id in feed_ids:
            if feed_id == self.master_feed_id:
                continue
            host = self.get_host_from_feed(feed_id)
            if (host == self.user_name): #host of this feed is also host of this app
                feed_names.append(self.get_feedname_from_id(feed_id))
        print(feed_names)
        return(feed_names)

    def set_path_to_db(self, path):
        os.chdir(path)
        f = open("testfile.txt", "w")
        f.write("hello")
        f.close

    def export_db_to_pcap(self, path):
        dictionary = {}
        feed_ids = self.get_all_feed_ids()
        for f_id in feed_ids:
            dictionary[f_id] = -1
        lm = LogMerge()
        lm.export_logs(path, dictionary)

    def import_from_pcap_to_db(self, path):
        lm = LogMerge()
        lm.import_logs(path)
        
    def get_all_feed_ids(self):
        return self.db_connector.get_all_feed_ids()
    
    def get_feedname_from_id(self, feed_id):
        print(self.get_event_content(feed_id, 1)[1]["list_name"])
        return self.get_event_content(feed_id, 1)[1]["list_name"]

    def get_host_from_feed(self, feed_id):
        return self.get_event_content(feed_id, 1)[1]["host"]

    def get_json_from_event(self, feed_id, seq_no):
        return self.get_event_content(feed_id, seq_no)[1]
    

        



