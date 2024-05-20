import logging
import sys
import os
import time
from threading import Thread, Timer, Lock
from concurrent import futures
import random

import grpc
import raft_pb2
import raft_pb2_grpc

ID = int(sys.argv[1])
server_Info = {}

logging.basicConfig(level=logging.DEBUG)

import builtins


class raftserver:
    old_leader_lease_times = {}
    max_old_leader_lease_time = 0
    voted_forid = -1
    term_global = -1

    def __init__(self):
        self.state = "Follower"
        self.term = 0
        self.id = ID
        self.voted = False
        self.leaderid = -1
        self.sleep = False
        self.timeout = None
        self.timer = None
        self.threads = []
        self.votes = []
        self.heartbeat_received = 0
        self.commitIndex = 0
        self.lastApplied = 0
        self.database = {}
        self.log = []
        self.nextIndex = []
        self.matchIndex = []
        self.leader_lease_time_to_heartbeat = 0
        self.leader_lease_time = 10
        self.leader_lease_timer = None
        self.lease_expired_flag = True
        self.leader_lease_start_time = None
        self.max_lease_from_followers = 0
        self.old_leader_lease_time = 0
        self.no_op_appended = False
        self.old_leader_lease_times = {}
        self.old_leader_lease_times_lock = Lock()
        self.start()
        self.write_logs()
        self.ff = None
        self.dump_file("")
        self.error_flag_heart = False
        self.error_flag_reuest = False
        self.comit_flag1 = False
        self.comit_flag2 = False

    def write_logs(self):
        logs_dir = f'logs_node_{self.id}'
        os.makedirs(logs_dir, exist_ok=True)
        with open(os.path.join(logs_dir, 'logs.txt'), 'w') as file:
            for entry in self.log:
                file.write(
                    f"Term: {entry['term']} {entry['update']['command']} {entry['update']['key']} {entry['update']['value']}\n")

    def append_log_entry(self):
        self.write_logs()

    def write_metadata(self):
        # global ff
        logs_dir = f'logs_node_{self.id}'
        with open(os.path.join(logs_dir, 'metadata.txt'), 'a') as file:
            file.write(f"CommitLength: {self.commitIndex}\n")
            # file.write(f"Term: {self.term}\n")
            # file.write(f"NodeID Voted For: {self.id}\n")

    def dump_file(self, message):
        logs_dir = f'logs_node_{self.id}'
        os.makedirs(logs_dir, exist_ok=True)
        with open(os.path.join(logs_dir, 'dump.txt'), 'a') as file:
            if message != "":
                file.write(f"{message} \n")

    def start(self):
        self.set_timeout()
        self.timer = Timer(0, self.follower_declaration)
        self.timer.start()
        # self.write_metadata()

    def set_timeout(self):
        if self.sleep:
            return
        self.timeout = random.uniform(5, 10)

    def restart_timer(self, time, func):
        self.timer.cancel()
        self.timer = Timer(time, func)
        self.timer.start()

    def update_state(self, state):
        self.state = state
        print(f'Term: {self.term}\t State: {self.state}')

    def update_term(self, term):

        self.voted = False
        self.term = term
        raftserver.term_global = self.term

        ###############
        metadata_dir = f"logs_node_{self.id}"
        os.makedirs(metadata_dir, exist_ok=True)
        metadata_file = os.path.join(metadata_dir, "metadata.txt")
        self.ff = open(metadata_file, "a")
        self.ff.write(f"Term: {self.term}\n")
        self.ff.close()

        print(
            f'\n-+-+-+-+-+- Term: {self.term} -+-+-+-+-+-\n')

    def follower_declaration(self):

        self.update_state("Follower")
        self.restart_timer(self.timeout, self.follower_action)

    def follower_action(self):
        if self.state != "Follower":
            return

        print(f'Term: {self.term}\t Leader is dead')
        self.leaderid = -1
        self.candidate_declaration()

    def candidate_declaration(self):

        self.update_term(self.term + 1)
        self.update_state("Candidate")
        self.voted = True
        self.leaderid = self.id

        # print(f'Term: {self.term}\t Voted_For: {self.id}')
        print(f'Vote Granted for :{self.id} in Term: {self.term}')
        self.dump_file(f'Vote Granted for :{self.id} in Term: {self.term}')
        self.restart_timer(self.timeout, self.candidate_action)
        self.candidate_election()

    def candidate_election(self):
        if self.state != "Candidate":
            return
        print(f'Node {self.id} election timer timed out, Starting election.')
        self.dump_file(f'Node {self.id} election timer timed out, Starting election.')

        self.votes = [0 for _ in range(len(server_Info))]
        self.threads = []
        for k, v in server_Info.items():
            if k == ID:
                self.votes[k] = 1
                continue
            self.threads.append(Thread(target=self.request, args=(k, v)))
        for t in self.threads:
            t.start()

    def candidate_action(self):
        if self.state != "Candidate":
            return

        for t in self.threads:
            t.join(0)

        print(
            f"Term: {self.term}\t Votes_Recieved: {sum(self.votes)}/{len(self.votes)}")

        if sum(self.votes) > ((len(self.votes) // 2)):
            self.timeout = 1
            if self.remaining_leader_lease_time() > 0:
                wait_time = self.remaining_leader_lease_time()
                print(f"Waiting for old leader's lease to expire ({wait_time} seconds)")
                self.dump_file(f"Waiting for old leader's lease to expire ({wait_time} seconds)")
                self.restart_timer(wait_time, self.leader_declaration)
            else:
                self.leader_declaration()
        else:
            self.set_timeout()
            self.follower_declaration()

    def leader_declaration(self):
        if self.sleep:
            return

        self.update_state("Leader")
        self.leaderid = self.id

        self.nextIndex = [(len(self.log) + 1) for i in server_Info]
        # print("next Index: ", self.nextIndex)
        self.matchIndex = [0 for i in server_Info]
        print("MAX_Received_by_leade: ", self.max_lease_from_followers)
        if not self.lease_expired():
            print("Waiting for old leader's lease to time out")
            self.dump_file(f"Waiting for old leader's lease to time out")
            wait_time = max(self.leader_lease_time, self.max_lease_from_followers)
            self.restart_timer(wait_time, self.start_lease_timer)
        else:
            self.start_lease_timer()
        print(f'Node {self.id} became the leader for term {self.term}.')
        self.dump_file(f'Node {self.id} became the leader for term {self.term}.')
        if not self.no_op_appended:
            print("Appending No-Op entry")
            self.log.append({"term": self.term, "update": {"command": '-', "key": "NO", "value": "OP"}})
            self.no_op_appended = True
        self.helper_heartbeat()
        print(f'Leader {self.id} sending heartbeat & Renewing Lease')
        self.dump_file(f'Leader {self.id} sending heartbeat & Renewing Lease')

    def start_lease_timer(self):
        self.leader_lease_start_time = time.time()
        self.lease_expired_flag = False
        self.leader_lease_timer = Timer(self.leader_lease_time, self.lease_expired_callback)
        self.leader_lease_timer.start()

    def lease_expired_callback(self):
        self.lease_expired_flag = True
        print(f'Leader {self.id} lease renewal failed. Stepping Down.')
        self.dump_file(f'Leader {self.id} lease renewal failed. Stepping Down.')
        # self.step_down()

    def lease_expired(self):
        return self.lease_expired_flag

    def remaining_leader_lease_time(self):
        if self.leader_lease_start_time is None:
            return 0
        elapsed_time = time.time() - self.leader_lease_start_time
        remaining_time = max(0, self.leader_lease_time - elapsed_time)
        return remaining_time

    def renew_lease(self):
        print(f"Term: {self.term}\t Renewing leader lease")
        if self.sleep or self.state != "Leader":
            return
        if self.leader_lease_timer:
            self.leader_lease_timer.cancel()
        self.start_lease_timer()

    def step_down(self):
        print(f"{self.id} Stepping down")
        self.follower_declaration()

    def helper_heartbeat(self):
        if self.state != "Leader":
            return
        # if self.heartbeat_received < ((len(self.votes) // 2)):
        #     print("dfadfdfdfd")
        #     self.step_down()
        #     return
        self.threads = []
        for k, v in server_Info.items():
            if k == ID:
                continue
            self.threads.append(Thread(target=self.heartbeat, args=(k, v)))
        for t in self.threads:
            t.start()
        self.leader_check()

    def leader_check(self):
        if self.state != "Leader":
            return

        for t in self.threads:
            t.join(0)

        self.nextIndex[ID] = len(self.log) + 1
        self.matchIndex[ID] = len(self.log)

        commits = sum(
            1 for element in self.matchIndex if element >= self.commitIndex + 1)
        print(self.heartbeat_received, "Heartbeats received")

        if commits > int(len(self.matchIndex) // 2):
            self.commitIndex += 1
            self.write_metadata()
        elif self.lease_expired():
            self.step_down()
        self.renew_lease()
        while self.commitIndex > self.lastApplied:
            key, value = self.log[self.lastApplied]["update"]["key"], self.log[self.lastApplied]["update"]["value"]
            self.database[key] = value
            print(f'Term: {self.term}\t {key} = {value}')
            self.lastApplied += 1
            print(f'Term: {self.term}\t Leader Node Id {self.id} committed the entry {key}={value}')
            self.dump_file(f'Term: {self.term}\t Leader Node Id {self.id} committed the entry {key}={value}')

        if self.heartbeat_received != 0:
            if self.heartbeat_received < ((len(self.votes) // 2)):
                print("dfadfdfdfd")
                self.step_down()
                # return
        self.heartbeat_received = 0
        self.restart_timer(self.timeout, self.helper_heartbeat)

    def request(self, id, address):
        if self.state != "Candidate":
            return

        channel = grpc.insecure_channel(address)
        stub = raft_pb2_grpc.RaftClientStub(channel)
        # print(self.log, len(self.log))
        # leader_lease_time_to_heartbeat = self.remaining_leader_lease_time()
        # with self.old_leader_lease_times_lock:
        #     old_leader_lease_time = self.old_leader_lease_times.get(id, 0)
        # self.old_leader_lease_time = leader_lease_time_to_heartbeat
        # print("@@@@@@@@@@@@@@@", old_leader_lease_time)
        message = raft_pb2.VoteRequest(term=int(self.term), id=int(self.id), last_log_index=len(
            self.log), last_log_term=(0 if len(self.log) == 0 else self.log[-1]["term"]))
        try:
            response = stub.RequestVote(message)
            reciever_term = response.term
            reciever_result = response.result
            # print("OLD_LEADE_LEASE: ", response.old_lease_time)
            # print(f"MAX_LEASE_FROM_FOLLOWERS:{1}", self.max_lease_from_followers)
            self.max_lease_from_followers = max(self.max_lease_from_followers, response.old_lease_time)
            # print(f"MAX_LEASE_FROM_FOLLOWERS:{2}", self.max_lease_from_followers)
            if reciever_term > self.term:
                self.update_term(reciever_term)
                self.set_timeout()
                self.follower_declaration()
            elif reciever_result:
                self.votes[id] = 1
        except grpc.RpcError:
            if self.error_flag_reuest == False:
                print(f"Error occurred while sending Request RPC to Follower Node .")
                self.dump_file(f"Error occurred while sending Request RPC to Follower Node .")
                self.error_flag_reuest = True

            return

    def heartbeat(self, id, address):
        if (self.state != "Leader"):
            return

        channel = grpc.insecure_channel(address)
        stub = raft_pb2_grpc.RaftClientStub(channel)

        entries = []
        if self.nextIndex[id] <= len(self.log):
            entries = [self.log[self.nextIndex[id] - 1]]

        prev_log_term = 0
        if self.nextIndex[id] > 1:
            prev_log_term = self.log[self.nextIndex[id] - 2]["term"]
        leader_lease_time_to_heartbeat = self.remaining_leader_lease_time()
        # print(leader_lease_time_to_heartbeat, "%%%%%%%%%%%%%%%%%%%")
        message = raft_pb2.AppendEntriesMessage(term=int(self.term), id=int(
            self.id), prev_log_index=self.nextIndex[id] - 1, prev_log_term=prev_log_term, entries=entries,
                                                leader_commit=self.commitIndex,
                                                lease_interval=leader_lease_time_to_heartbeat, heartbeat_count=0)
        try:
            response = stub.AppendEntries(message)
            reciever_term = response.term
            reciever_result = response.result
            old_leader_lease_time = response.storing_leasder_lease_time
            # print(old_leader_lease_time, "@@@@@@@@@@@@@@@")
            self.heartbeat_received = response.heartbeat_count + self.heartbeat_received
            print(self.heartbeat_received, "$$$$$$$$")
            if reciever_term > self.term:
                self.update_term(reciever_term)
                self.set_timeout()
                self.follower_declaration()
            else:
                if reciever_result:
                    if len(entries) != 0:
                        self.matchIndex[id] = self.nextIndex[id]
                        self.nextIndex[id] += 1
                else:
                    self.nextIndex[id] -= 1
                    self.matchIndex[id] = min(
                        self.matchIndex[id], (self.nextIndex[id] - 1))
        except grpc.RpcError:
            if self.error_flag_heart == False:
                print(f"Error occurred while sending Append RPC to Follower Node .")
                self.dump_file(f"Error occurred while sending Append RPC to Follower Node .")
                self.error_flag_heart = True
            return

    def gotosleep(self, period):
        self.sleep = True
        print(f'Term: {self.term}\t Sleeping for {period} seconds')
        self.restart_timer(int(period), self.wakeup)

    def wakeup(self):
        self.sleep = False
        self.follower_declaration()


class RaftServer(raft_pb2_grpc.RaftClientServicer, raftserver):
    def _init_(self):
        super().__init__()

    def GetStatus(self, request, context):
        if self.sleep:
            context.set_details("Server suspended")
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return "Server suspended"
        reply = {}
        print(f'Term: {self.term}\t Command: getStatus')

        return raft_pb2.EmptyMessage()

    def GetLeader(self, request, context):

        print(f'Term: {self.term}\t Command: getleader')

        if self.leaderid != -1:
            return raft_pb2.LeaderMessage(leader=int(self.leaderid), address=server_Info[self.leaderid])
        return raft_pb2.LeaderMessage(leader=int(self.leaderid), address="No address")

    def GetVal(self, request, context):
        print(f"Node {self.leaderid}  received a GET request from client.")
        self.dump_file(f"Node {self.leaderid}  received a GET request from client.")
        if request.leader_id_start != self.leaderid:
            context.set_details(f"Leader mismatch. New leader ID: {self.leaderid}")
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            return raft_pb2.ServeClientReply(success=True, leader_id=int(self.leaderid), message="Leader mismatch")
        if request.key in self.database:
            return raft_pb2.ServeClientReply(success=True, leader_id=int(self.leaderid),
                                             data=self.database[request.key])
        return raft_pb2.ServeClientReply(success=False, leader_id=int(self.leaderid),
                                         message="request.key not found in database")

    def SetVal(self, request, context):

        print(f"Node {self.leaderid} received a SET request from client.")
        self.dump_file(f"Node {self.leaderid} received a SET request from client.")

        if self.state == "Leader":
            self.log.append({"term": self.term, "update": {
                "command": 'set', "key": request.key, "value": request.value}})
            self.append_log_entry()
            return raft_pb2.Success(success=True)
        elif self.state == "Follower":
            # print("#########################")
            channel = grpc.insecure_channel(f'{server_Info[self.leaderid]}')
            stub = raft_pb2_grpc.RaftClientStub(channel)
            message = raft_pb2.Set_Key_Val(key=request.key, value=request.value)
            try:
                response = stub.SetVal(message)
                return raft_pb2.Success(success=response.success)
            except grpc.RpcError:
                print("Server is not avaliable")

        return raft_pb2.Success(success=False)

    def RequestVote(self, request, context):

        reply = {"term": -1, "result": False, "old_lease_time": self.old_leader_lease_time}
        if request.term == self.term:
            if self.voted or request.last_log_index < len(self.log) or self.state != "Follower":
                reply = {"term": int(self.term), "result": False, "old_lease_time": self.old_leader_lease_time}
            elif request.last_log_index == len(self.log):
                if self.log[request.last_log_index - 1]["term"] != request.last_log_term:
                    reply = {"term": int(self.term), "result": False, "old_lease_time": self.old_leader_lease_time}
            else:
                self.voted = True
                self.leaderid = request.id
                print(f'Term: {self.term}\t Followere {self.id} Granted Vote For: {request.id}')
                self.dump_file(f'Term: {self.term}\t Followere {self.id} Granted Vote For: {request.id}')
                metadata_dir = f"logs_node_{self.id}"
                os.makedirs(metadata_dir, exist_ok=True)
                metadata_file = os.path.join(metadata_dir, "metadata.txt")
                self.ff = open(metadata_file, "a")
                self.ff.write(f"Term: {self.term}\t Voted_For: {request.id}\n")
                self.ff.close()

                reply = {"term": int(self.term), "result": True, "old_lease_time": self.old_leader_lease_time}

            if self.state == "Follower":
                self.restart_timer(self.timeout, self.follower_action)


        elif request.term > self.term:
            self.update_term(request.term)
            print(f'Term: {self.term}\t Followere {self.id} Granted Vote For: {request.id}')
            self.dump_file(f'Term: {self.term}\t Followere {self.id} Granted Vote For: {request.id}')
            metadata_dir = f"logs_node_{self.id}"
            os.makedirs(metadata_dir, exist_ok=True)
            metadata_file = os.path.join(metadata_dir, "metadata.txt")
            self.ff = open(metadata_file, "a")
            self.ff.write(f"Term: {self.term}\t Follower {self.id} Granted Voted For: {request.id}\n")
            self.ff.close()
            self.leaderid = request.id
            self.voted = True
            self.follower_declaration()
            reply = {"term": int(self.term), "result": True, "old_lease_time": self.old_leader_lease_time}

        else:
            reply = {"term": int(self.term), "result": False, "old_lease_time": self.old_leader_lease_time}
            if self.state == "Follower":
                self.restart_timer(self.timeout, self.follower_action)

        return raft_pb2.VoteRequestResponse(**reply)

    def AppendEntries(self, request, context):

        self.old_leader_lease_time = request.lease_interval
        reply = {"term": -1, "result": False, "storing_leasder_lease_time": self.old_leader_lease_time,
                 "heartbeat_count": 1}

        if request.term >= self.term:
            if request.term > self.term:
                self.update_term(request.term)
                self.follower_declaration()
                self.leaderid = request.id

            if len(self.log) < request.prev_log_index:
                reply = {"term": int(self.term), "result": False,
                         "storing_leasder_lease_time": self.old_leader_lease_time, "heartbeat_count": 1}
                print(f"Node {self.id} rejected AppendEntries RPC from {request.id}.")
                self.dump_file(f"Node {self.id} rejected AppendEntries RPC from {request.id}.")
                # if self.state == "Follower":
                #     self.restart_timer(self.timeout, self.follower_action)

            else:
                if len(self.log) > request.prev_log_index:
                    self.log = self.log[:request.prev_log_index]

                if len(request.entries) != 0:
                    print(f"Node {self.id} accepted AppendEntries RPC from {request.id}")
                    self.dump_file(f"Node {self.id} accepted AppendEntries RPC from {request.id}")
                    self.log.append({"term": request.entries[0].term, "update": {
                        "command": request.entries[0].update.command, "key": request.entries[0].update.key,
                        "value": request.entries[0].update.value}})
                    self.append_log_entry()

                if request.leader_commit > self.commitIndex:
                    self.commitIndex = min(
                        request.leader_commit, len(self.log))
                    # if self.comit_flag2 == False:
                    #     self.write_metadata()
                    #     self.comit_flag2 = True
                    while self.commitIndex > self.lastApplied:
                        key, value = self.log[self.lastApplied]["update"]["key"], self.log[self.lastApplied]["update"][
                            "value"]
                        self.database[key] = value
                        print(f'Term: {self.term}\t {key} = {value}')
                        self.lastApplied += 1
                        print(f"Node {self.id} committed the entry {key}= {value} to the state machine")
                        self.dump_file(f"Node {self.id} committed the entry {key}= {value} to the state machine")
                if self.comit_flag1 == False:
                    metadata_dir = f"logs_node_{self.id}"
                    os.makedirs(metadata_dir, exist_ok=True)
                    metadata_file = os.path.join(metadata_dir, "metadata.txt")
                    self.ff = open(metadata_file, "a")
                    self.ff.write(f"Commit Index {self.commitIndex}\n")
                    self.ff.close()
                    self.comit_flag1 = True

                reply = {"term": int(self.term), "result": True,
                         "storing_leasder_lease_time": self.old_leader_lease_time, "heartbeat_count": 1}
                self.restart_timer(self.timeout, self.follower_action)
        else:
            reply = {"term": int(self.term), "result": False, "storing_leasder_lease_time": self.old_leader_lease_time,
                     "heartbeat_count": 1}
        return raft_pb2.AppendEntryReply(**reply)

    def server(self):
        print(f'Server ID: {ID}')
        print(f'Server Address: {server_Info[ID]}')
        print(f'================================\n')
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        raft_pb2_grpc.add_RaftClientServicer_to_server(self, self.server)
        print(server_Info[ID])
        self.server.add_insecure_port(f"[::]:{server_Info[ID].split(':')[-1]}")
        print("Server started Listning....")
        # server.wait_for_termination()
        try:
            self.server.start()
            while True:
                self.server.wait_for_termination()
        except KeyboardInterrupt:
            print("Shutting Down")
            os._exit(0)


if __name__ == '__main__':
    ids = [0, 1, 2, 3, 4]
    addresses = ["localhost", "localhost", "localhost", "localhost", "localhost"]
    ports = ["50000", "50001", "50002", "50003", "50004"]
    for i in range(5):
        server_Info[ids[i]] = f'{addresses[i]}:{ports[i]}'
    node = RaftServer()
    node.server()
