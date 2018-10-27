from concurrent import futures;
import grpc;
import time;

import messenger_pb2 as chat;
import messenger_pb2_grpc as rpc;
import yaml;
import lrucache;

with open("config.yaml", 'r') as stream:
    try:
        yaml_file = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

port = yaml_file['port']
max_num_messages = yaml_file['max_num_messages_per_user']
rate_limit = yaml_file['max_call_per_30_seconds_per_user']
users = yaml_file['users']

rate_limit_time = 30

class ChatServer(rpc.ChatServerServicer):

    def __init__(self):

        self.cache = {}
        self.messages = {}
        self.unreadMessages =  {}
        self.registeredUsers = []
        self.sent_num_messages = {}
        self.requestFromUser = {}
        for usr in yaml_file['users']:
            self.registeredUsers.append(chat.User(name=usr))
            self.unreadMessages[usr] = {}
            self.sent_num_messages[usr] = []

    def CreateConnection(self, request: chat.User, context):
        users = [request.name, request.othername]
        self.requestFromUser[request.othername] = chat.User(name=request.name)
        users.sort()
        new_key = users[0] + "-" + users[1]
        
        for online_user in self.registeredUsers:
            if (online_user.name == request.othername):
                if new_key not in self.messages:
                    self.messages[new_key] = lrucache.LRUCache(max_num_messages)
                return chat.Connection(successful=True)
        return chat.Connection(successful=False)

    def CheckMessageList(self, request, context):
        if request.name in self.requestFromUser:
            return self.requestFromUser[request.name]
        else:
            return chat.User(name="NA")

    def rateLimit(self, user, current_time):

        num_messages = len(self.sent_num_messages[user])

        if num_messages == 0:
            self.sent_num_messages[user].append(current_time)
            return True
        
        for i in range(0, num_messages):
            time_interval = current_time - self.sent_num_messages[user][i]
            
            if num_messages == rate_limit:
                if time_interval <= rate_limit_time:
                    return False
                else:
                    i = i + 1
            else:
                if time_interval > rate_limit_time:
                    i = i + 1
                else:
                    break

        self.sent_num_messages[user] = self.sent_num_messages[user][i:]
        self.sent_num_messages[user].append(current_time)
        return True

    def SendMessage(self, request: chat.Msg, context):

        current_time = time.time()
        
        users = [request.name, request.othername]
        sorted_users = sorted(users)
        dict_key = sorted_users[0] + '-' + sorted_users[1]

        isUnderLimit = self.rateLimit(users[0], current_time)

        if isUnderLimit:
            self.messages[dict_key].set(current_time, (request))
            if self.unreadMessages[users[0]][users[1]] < max_num_messages:
                self.unreadMessages[users[0]][users[1]] += 1
            if self.unreadMessages[users[1]][users[0]] < max_num_messages:
                self.unreadMessages[users[1]][users[0]] += 1
            yield(chat.WarningMsg(warning=""))
        else:
            yield(chat.WarningMsg(warning="[Spartan] WARNING: You cannot send more messages. You have crossed the rate limit."))
    
    def ChatStream(self, request: chat.User, context):

        n = chat.Msg()
        users = [request.name, request.othername]
        sorted_users = sorted(users)
        my_key = sorted_users[0] + '-' + sorted_users[1]
        key2 = users[0] + '-' + users[1]
        n.name = users[0]
        n.othername = users[1]

        sender = users[0]
        receiver = users[1]

        #using lru cache to stream new messages

        while True:

            if self.unreadMessages[sender].get(receiver) == None:
                self.unreadMessages[sender][receiver] = 0
            if self.unreadMessages[receiver].get(sender) == None:
                self.unreadMessages[receiver][sender] = 0

            if(my_key in self.messages):
                new_messages = self.messages[my_key].show()

                while self.unreadMessages[sender][receiver] > 0:
                    index = len(new_messages) - self.unreadMessages[sender][receiver]
                    try:
                        n = new_messages[index]
                    except KeyError:
                        continue

                    if self.unreadMessages[sender][receiver] > 0:
                        self.unreadMessages[sender][receiver] -= 1
                    yield n
            time.sleep(0.1)
                
if __name__ == '__main__':

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)
    print('[Spartan] Connected to Spartan Server at port {}.'.format(port))
    server.add_insecure_port('[::]:' + str(port))
    server.start()

    while True:
        time.sleep(64 * 64 * 100)