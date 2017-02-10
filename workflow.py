import re
import numpy as np
import itertools
import pdb

from node import Node

# TODO: Node should be used?
class Workflow():
    # TODO: inputs should be in the init?
    def __init__(self, nodes_list=None, inputs_map={}, output_map={}, name=None):
        if nodes_list:
            self.nodes_list = nodes_list
        else:
            self.nodes_list = []
        self.name = name
        self.inputs_map = inputs_map
        self.output_map = output_map
        self.connect_inp = {}

    def add_node(self, new_node):
        self.nodes_list.append(new_node)
        if new_node.inputs:
            self.inputs_map.update(new_node.inputs)
        if not new_node.name:
            new_node.name = "node"+str(len(self.nodes_list))


    def connect(self, from_node, from_socket, to_node, to_socket):
        # TODO spr order in the list?
       if from_node not in self.nodes_list:
            self.add_node(from_node)
       if to_node not in self.nodes_list:
            self.add_node(to_node)
        
       if not to_node.name in self.connect_inp.keys():
           self.connect_inp[to_node.name] = []
       inp = View(from_node.output)
       inp.rename(from_socket,to_socket)
       self.connect_inp[to_node.name].append(inp)
       #to_node.inputs.rename(from_node, to_node)


    # TODO think about order/graph
    def run(self):
        for nn in self.nodes_list:
            if nn.name in self.connect_inp.keys():
                self._update_inputs(nn)
            pdb.set_trace()
            nn.run()
            self.output_map[nn.name] = nn.output
            

    def _update_inputs(self, node):
        inp = node.inputs
        for dict in self.connect_inp[node.name]:
            for (key, val) in dict.items():
                inp[key] = val
        node.inputs = inp


# TODO test it
class View(object):
    def __init__(self, d):
        self._d = d
        self._renaming = {}

    def rename(self, a, b):
        self._renaming[b] = a

    def __getitem__(self, key):
        return self._d[self._renaming[key]]

    def items(self):
        for (key, it) in self._renaming.items():
            yield (key,self._d[self._renaming[key]])



# przy connect tworzyc sn1.output["a"] = none
# i sn2.input["aa"] = sn1.output["a"]
