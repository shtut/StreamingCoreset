#Streaming Core-Set (Client-Server)

__**General Description:**__

A Server-Client python module which cluster streaming data and generate a final 'Core-Set'. The 'Core-Set' provides a small representation of the large data. The project was based on Big Data methodologies using deep learning algorithms on Amazon AWS (mainly Amazon EC2).


__**Design Description:**__

The system is designed to cluster large amounts of data in streaming format.

The system is made of 3 main parts-

1. The Server
2. The Client
3. The Worker

__It works in the following manner:__

![alt tag](https://raw.githubusercontent.com/shtut/StreamingCoreset/master/StremingCoreset/Documentation/website/media/design2.png)

The client provides the data to the server, streaming it via socket communication.
The server then collects the data and distributes it to the workers.
Each worker creates a core-set from its given data.  So that in every moment each worker has a corset of the data it received so far.


Upon request from the client, the server collects all the current core-sets from all the workers and sends them to the summary worker- a dedicated worker which creates the final core-set, and sends it back to the server.

The server then returns the final core-set to the client, and we receive a representing smaller portion of the streamed data.
