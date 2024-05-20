import sys

import grpc
import raft_pb2
import raft_pb2_grpc

server_Info = {}

Leader_start = -1


def connection():
    for id, addresses in server_Info.items():
        channel = grpc.insecure_channel(addresses)
        stub = raft_pb2_grpc.RaftClientStub(channel)
        message = raft_pb2.EmptyMessage()
        try:
            status = stub.GetStatus(message)
            print(f'Connected to server {id}\n')
            return stub
        except grpc.RpcError as e:
            print(f"Error connecting to server {id}: {e}")
            pass
    print("No servers are available\n")


def get_leader(stub):
    stub = connection()
    message = raft_pb2.EmptyMessage()
    try:
        response = stub.GetLeader(message)
        if response:
            leader = response.leader
            leader_address = response.address
            print(f'ID: {leader}\t Address: {leader_address}')
            return leader
        else:
            print(f'Nothing\n')
    except grpc.RpcError:
        print("Server is not avaliable\n")


def get(key, stub, input_buffer, leader_start):
    stub = connection()
    request = raft_pb2.ServeClientArgs(input=input_buffer)
    message = raft_pb2.Get_Key(key=key, leader_id_start=leader_start)
    response = stub.GetVal(message)
    if not response.success:
        print("Dsfasdf")
        print(response.message, ":", f"New Leader is{response.leader_id}")
    else:
        print(f'{key} = {response.data}')
    # try:
    #     response = stub.GetVal(message)
    #     if not response.success:
    #         print(response.message, ":", f"New Leader is{response.leader_id}")
    #     print(f'{key} = {response.data}')
    # except grpc.RpcError as e:
    #     print(f"Error getting value: {e}")


def set(key, value, stub):
    stub = connection()
    message = raft_pb2.Set_Key_Val(key=key, value=value)
    try:
        response = stub.SetVal(message)
        if response.success:
            pass
        else:
            print("Something went wrong, try again later\n")
    except grpc.RpcError:
        print("Server is not available\n")


def client():
    print("Client Started\n")
    stub = connection()
    Leader_start = get_leader(stub)
    while True:
        try:
            input_buffer = input("> ")

            command = input_buffer.split()[0]
            command_args = input_buffer.split()[1:]
            # response = stub.ServeClient(request)
            # print(response)
            if command == "getleader":
                get_leader(stub)
            elif command == "getval":
                get(command_args[0], stub, input_buffer, Leader_start)
            elif command == "setval":
                set(command_args[0], command_args[1], stub)
            elif command == "quit":
                print("Client Stopped\n")
                sys.exit()
            else:
                print(f'command: {command}, is not supported\n')
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    ids = [0, 1, 2, 3, 4]
    # addresses = ["localhost", "localhost", "localhost"]
    # ports = ["50000", "50001", "50002"]
    addresses = ["localhost", "localhost", "localhost", "localhost", "localhost"]
    ports = ["50000", "50001", "50002", "50003", "50004"]

    for i in range(5):
        server_Info[ids[i]] = f'{addresses[i]}:{ports[i]}'
    print(server_Info)
    client()
