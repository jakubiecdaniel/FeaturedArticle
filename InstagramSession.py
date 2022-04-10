
import json
class InstagramSession: 
    '''
    session =   {
        "csrf_token": "CSRF_TOKEN",
        "session_id": "SESSION_ID",
        "ds_user_id": "DS_USER_ID",
        "ig_did"    : "IG_DID",
        #"ig_nrcb"   : "IG_NRCB",
        "mid"       : "MID",
        "rur"       : "RUR",
    }       
    '''

    def __init__(self,session_dict=None):
        if session_dict:
            for key in session_dict:
                self.session[key] = session_dict[key]
        else:
            self.session = {}

    
    def set_value(self,key,value):
        self.session[key] = value

    def get_value(self,key):

        if key in self.session:
            return self.session[key]
        return None


    def update_session(self,new_session):
        for key in new_session:
            self.session[key] = new_session[key]

    def overwrite_session(self,new_session):
        self.session = new_session

    def write_to_file(self):
        f = open("config", "w")
        f.write(json.dumps(self.session))
        f.close()

    def update_file(self):
        try:
            f = open("config","r")
        except:
            print("Config file not found, load it first.")
            return False
        s_t = json.loads(f.read())
        f.close()

        for key in self.session:
            s_t[key] = self.session[key]

        f = open("config", "w")
        f.write(json.dumps(s_t))
        f.close()

    def add_to_file(self,key,value):
        try:
            f = open("config","r")
        except:
            print("Config file not found, load it first.")
            return False
        s_t = json.loads(f.read())
        s_t[key] = value
        f.close()

        f = open("config", "w")
        f.write(json.dumps(s_t))
        f.close()
        
        

    def load_from_file(self):
        try:
            f = open("config","r")
        except:
            print("Config file not found, load it first.")
            return False
        self.session = json.loads(f.read())
        f.close()
        return True

