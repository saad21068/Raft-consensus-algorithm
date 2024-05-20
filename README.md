# Overview
This project implements a modified RAFT consensus algorithm with leader leases to improve read performance in a geo-distributed database. The database stores key-value pairs and ensures fault tolerance and consistency across multiple nodes.

# Introduction
The RAFT application is designed to demonstrate a distributed key-value store using the RAFT consensus algorithm. The implementation includes a modification to the standard RAFT algorithm to use leader leases, which reduces the latency of read operations.

# Features
1) Leader election and term management
2) Log replication with strong consistency
3) Fault-tolerant design
4) Leader leases for faster read operations
5) Persistence of logs and metadata
6) gRPC-based communication

# Setup
## Prerequisites
1. Python 3.8+
2. grpcio and grpcio-tools for gRPC communication
3. Google Cloud VMs (for running nodes on separate virtual machines)
# Installation

1. Clone the repository:

```bash
git clone https://github.com/saad21068/Raft-consensus-algorithm/
```
2. Install required Python packages:

```bash
pip install -r requirements.txt
```
3. Set up gRPC protobufs:
```bash
python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. raft.proto
```
# Running the Application
## Starting the Cluster
1. Start the RAFT nodes on separate VMs (or locally on different ports for testing):
```bash
start 5 VMs (for example 5 node) in Google Cloud different VM
```
2. Start the client to interact with the cluster:
```bash
python client.py
```
# Performing Operations
1. SET operation: Store a key-value pair
```bash
SET key value
```
2. GET operation: Retrieve the value for a key
```bash
GET key
```
# File Structure
```bash
├── node.py                 # RAFT node implementation
├── client.py               # Client to interact with RAFT nodes
├── raft.proto              # Protobuf definitions for gRPC
├── logs_node_x/            # Logs and metadata for each node
│   ├── logs.txt
│   ├── metadata.txt
│   ├── dump.txt
├── README.md               # This README file
├── requirements.txt        # Python dependencies
└── ...
```
# Important Notes
1. Ensure all nodes and the client have the correct IP addresses and ports configured.
2. Logs and metadata are persisted in the logs_node_x directories to ensure durability.
