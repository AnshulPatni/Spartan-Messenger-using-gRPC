# Spartan-Messenger-using-gRPC

This repository is to build a bidirectional chat application, a Spartan Messenger, using GRPC in Python3. We want to use gRPC response streaming to continuously receive chat messages from the Spartan server.

__gRPC__ is a modern, open source, high-performance remote procedure call (RPC) framework that can run anywhere. It enables client and server applications to communicate transparently, and makes it easier to build connected systems.

<table>
  <tr>
    <td><b>Homepage:</b></td>
    <td><a href="https://grpc.io/">grpc.io</a></td>
  </tr>
  <tr>
    <td><b>For more information:</b></td>
    <td><a href="https://github.com/grpc">github.com/grpc</a></td>
  </tr>
</table>

> A response-streaming RPC where the client sends a request to the server and gets a stream to read a sequence of messages back. The client reads from the returned stream until there are no more messages. As you can see in the example, you specify a response-streaming method by placing the stream keyword before the response type.
// Obtains the Features available within the given Rectangle.  Results are
// streamed rather than returned at once (e.g. in a response message with a
// repeated field), as the rectangle may cover a large area and contain a
// huge number of features.
```
rpc ReceiveMsg(Message) returns (stream Message) {} 
```

## Features
 
- Design one-on-one conversations between users. :couple:

Run Spartan Server
```sh
python3 server.py
Spartan server started on port 3000.
```

Alice's Terminal
```sh
> python3 client.py alice
[Spartan] Connected to Spartan Server at port 3000.
[Spartan] User list: bob,charlie,eve,foo,bar,baz,qux
[Spartan] Enter a user whom you want to chat with: bob
[Spartan] You are now ready to chat with bob.
[alice] > Hey Bob!
[alice] >
```

Bob's Terminal
```sh
> python3 client.py bob
[Spartan] Connected to Spartan Server at port 3000.
[Spartan] User list: alice,charlie,eve,foo,bar,baz,qux
[Spartan] alice is requesting to chat with you. Enter 'yes' to accept or different user: yes
[Spartan] You are now ready to chat with alice.
[alice] Hey Bob!
[bob] >
```

Bob's Terminal
```sh
...
[bob] > Hi Alice!
[bob] >
```

Alice's Terminal
```sh
...
[bob] Hi Alice!
[alice] >
```


- Implements a LRU Cache to store recent messages in memory. :floppy_disk:
- Limit the number of messages a user can send to an API within a time window e.g., 15 requests per second. NOTE: The rate limiting should work for a distributed setup. :vertical_traffic_light:



- Provide end-to-end message encryption using [AES from PyCrypto library](https://docs.python-guide.org/scenarios/crypto/#pycrypto). :key: 
- Add [Decorator](https://www.python-course.eu/python3_decorators.php) for the LRU cache (E.g @lru_cache) and rate limition (E.g. @rate) from the level :star:. :cyclone:

__Future Work__
- Extend your design to support group chats. :family: [3 points]

## App Config

- Use given [config.yaml](config.yaml) to load users for the Spartan messenger.