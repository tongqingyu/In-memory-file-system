# In-memory-file-system
The memoryfs.py file (which is seperated into memoryfs_client.py and memoryfs_server.py in the later updates) implements the file system objects.
The memoryfs_shell.py imports memoryfs, and implements a rudimentary "shell" for interactive access to the file system.
Use "dump" file 12345678_BS_128_NB_256_IS_16_MI_16.dump with preloaded contents for blocks.

Involved practical issues: client/service, networking, and fault tolerance.

## Version 1

#### Overall
Originally, the shell only implements the "cd" command. In this version, I add "cat" command and "ls" command. 
I implement READ method in memoryf.py to support these command. 

#### Details
- The "cat" command takes filesname as the argument and print the content of the file. 
- The "ls" command takes no argument, it traverses the data blocks of the current working directory and prints out the name of each files(file or directory).
- The Read method takes file_inode takes file_inode_number, offest and count as the parameters; file_inode_number is the inode number of the file in the file system; offset is the starting point to read from and count is the number of bytes needed to read.

## Version 2

#### Overall
Extend my system to support the path name layer, Link and more commands including "mkdir", "create", "append" and "ln".

#### Details
- I add two methods in FileName() class to support name layer. The first method is PathToInodeNumber which takes path and dir as parameters. This supports lookups for path name, with "/" as the seperator, path is string and dir is the inode number of the directory. The second method is GeneralPathToInodeNumber which takes path and cwd(inode of current working directory) as parameters; this allows using a leading "/" to refer to the absolute path.
- I add Link method to FileName() class. It takes target, name and cwd as parameters; target is a string with a path to the file to link to, name is the name of the link and ced is the current directory.
- The command "mkdir" creatate of a new directory.
- The command "create" create of a new file.
- The command "append" appends a string to a file.
- The command "ln" creates a link to target, with name linkname, in the cwd.

## Version 3

#### Overall
In this stage, I seperate the system into client side and server side with the use of XML-RPC.

#### Note
XML-RPC is a remote procedure call (RPC) protocol which uses XML to encode its calls and HTTP as a transport mechanism. In this version, we need to consider the situation that multiple clients call the server at the same time. So we introduce a lock to the system.

#### Details
- The server holds the file system data. The main RPC functions are ReadSetBlock(), Get() and Put(). Get(block_number) returns a block, given its number; Put(block_number,data) writes a block, given its number and data contents. ReadSetBlock(block_number,data)reads a block, sets the block contents to a LOCKED value and returns the block read.
- Replace the Get() and Put() primitives to Get() and Put() calls to the server.
- Design and implement an approach that prevents race conditions by implementing a lock.

## Version 4

#### Overall
I extend my client/server based file system to multiple servers with support for redundant block storage. I identify the servers using integers. The number of server supported is four to eight. In this version, we set the number of clients as one for simplicity, therefore the use of lock could be ignored.

#### Note
RAID 5 consists of block-level striping with distributed parity. Unlike in RAID 4, parity information is distributed among the drives. It requires that all drives but one be present to operate. Upon failure of a single drive, subsequent reads can be calculated from the distributed parity such that no data is lost

#### Detail
- My redundant block storage follow the general approach described for RAID-5 aiming to reduce load of single server, provide increased aggregate capacity and increase fault-tolerance.
- I implement 128-bit MD5 as checksums to detect single block error and I store checksum for multiple data block in a single checksum block.
- Reads allow for load-balancing, distributing requests across the servers holding data for different blocks. The reads detect checksum first. If data in a single server/block is detected as corrupt, the system will use other server's blocks and parity to correct the error.
- Writes update both the data and parity block. If one of the servers fails, the system own the ability to continue future operations using remaining servers. 
