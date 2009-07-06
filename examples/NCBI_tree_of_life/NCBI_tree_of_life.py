#!/usr/bin/env python 

print """ 
This program reads the NCBI taxonomy database (text file format) and
reconstruct the whole taxonomy tree of life. Once loaded, the progrmas
allows you to look up for the specific subtree of a given taxid, or
save the tree in newick format.

Note that reconstructing the from the raw NCBI format may take some
minutes.
"""

import os
import sys 
from string import strip
from ete2 import TreeNode

# This sets Unbuffered stdout/auto-flush
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

id2node= {}
node2parentid = {}
all_ids = set([])
all_nodes = []
id2name= {}

# Loads info from NCBI taxonomy files
if os.path.exists("nodes.dmp"):
    NODESFILE = open('nodes.dmp')
elif os.path.exists("nodes.dmp.bz2"):
    import bz2
    NODESFILE = bz2.BZ2File('nodes.dmp.bz2')
else:
    print '"nodes.dmp" file is missing. Try to downloaded from: '

if os.path.exists("names.dmp"):
    NAMESFILE = open('names.dmp')
elif os.path.exists("names.dmp.bz2"):
    import bz2
    NAMESFILE = bz2.BZ2File('names.dmp.bz2')
else:
    print '"names.dmp" file is missing. Try to downloaded from: '

# Reads taxid/names transaltion
print 'Loading species names from "names.dmp" file...',
for line in NAMESFILE:
    line = line.strip()
    fields = map(strip, line.split("|"))
    nodeid, name = fields[0], fields[1]
    id2name[nodeid] = name

print len(id2name)

# Reads node connections in nodes.dmp
print 'Loading node connections form "nodes.dmp" file...', 
for line in NODESFILE:
    line = line.strip()
    fields = map(strip, line.split("|"))
    nodeid, parentid = fields[0], fields[1]
    if nodeid =="" or parentid == "":
	raw_input("Wrong nodeid!")

    # Stores node connections
    all_ids.update([nodeid, parentid])

    # Creates a new TreeNode instance for each new node in file
    n = TreeNode()
    # Sets some TreeNode attributes
    n.add_feature("name", id2name[nodeid])
    n.add_feature("taxid", nodeid)

    # updates node list and connections
    node2parentid[n]=parentid
    id2node[nodeid] = n
print len(id2node)

# Reconstruct tree topology from previously stored tree connections
print 'Reconstructing tree topology...'
for node in id2node.itervalues():
    parentid = node2parentid[node]
    parent = id2node[parentid]
    # node with taxid=1 is the root of the tree
    if node.taxid == "1":
	t = node
    else:
        parent.add_child(node)

# Let's play with the tree
print "The tree contains %d leaf species" %len(t)
taxid = None
while taxid!='':
    print "================================================="
    taxid = raw_input("Choose the taxid of any taxa group (hit ENTER to quit)\n"+\
			  "Old taxa produces huge trees [e.g. Primates: 9443]:").strip()
    if taxid in id2name:
	print "Searching for the subtree of: ", id2name[taxid]
	# Node matching the given taxid can be found in the main dict.
	target_node =  id2node[taxid]
	# However, it could also be found by doing:
	# taget_node=t.search_nodes(taxid=whatever)[0] #(Although it
	# would slower)
	print target_node
    else:
	print "taxid not found"
    print 

save = None
while save!='y' and save!='n':
    save = raw_input("Do you want to save the tree using the newick format?[y|n]").strip().lower()
if save=='y':
    print "Saving tree. This may take some minutes..."
    open("tree.nw", "w").write( t.write(features=["name","taxid"]) )
    print "tree.nw has been created."

