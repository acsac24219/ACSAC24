import json
import sys
import re
import queue
from pprint import pprint
from collections import OrderedDict
from urllib.parse import urlparse
from cpgqls_client import CPGQLSClient, import_code_query, workspace_query
from jproperties import Properties
import time


import tool


cpg_dict={}

new_var_stack = []
global_var_value_dict = {}
method_url_dict = {}

def getDataFlow():
    global new_var_stack
    global global_var_value_dict
    global method_url_dict

    query='cpg.call.name("connect").id.toJson'
    result=tool.formatJoernResult(tool.joern_client.execute(query))

    for call_id in result:
        mysql_query='cpg.call.id(%s).code(".*query.*").id.toJson'%(call_id)
        mysql_result=tool.formatJoernResult(tool.joern_client.execute(mysql_query))
        if mysql_result and call_id == mysql_result[0]:
            control_query='cpg.call.id(%s).controlledBy.code.toJson'%(call_id)
            control_result=tool.formatJoernResultNew(tool.joern_client.execute(control_query))
            tmp={"entry":"/^\\/ratings\\/[0-9]*/","send_request":"mysql","condition":control_result,"dependence":[]}
            pprint(tmp)

        mongo_query='cpg.call.id(%s).code(".*collection.*").id.toJson'%(call_id)
        mongo_result=tool.formatJoernResult(tool.joern_client.execute(mongo_query))
        if mongo_result and call_id == mongo_result[0]:
            control_query='cpg.call.id(%s).controlledBy.code.toJson'%(call_id)
            control_result=tool.formatJoernResultNew(tool.joern_client.execute(control_query))
            tmp={"entry":"/^\\/ratings\\/[0-9]*/","send_request":"mongo","condition":control_result,"dependence":[]}
            pprint(tmp)



def openProject(inputPath,projectName):
    # query = import_code_query(inputPath,projectName)
    query = 'importCode(inputPath="%s", projectName="%s")'%(inputPath,projectName)
    result = tool.joern_client.execute(query)
    # pprint(result)

    query="run.ossdataflow"
    result = tool.joern_client.execute(query)
    # pprint(result)



def runJoern(inputPath,projectName):

    openProject(inputPath,projectName)


    #todo get needed var (program slicing)
    start=time.time()
    getDataFlow()
    # print("parse time:%f"%(time.time()-start))

if __name__ == '__main__':
    # if 3!=len(sys.argv):
    #     print("Usage: python3 parse_multi_hop.py <inputPath> <projectName>")
    #     exit(-1)
    # runJoern(sys.argv[1],sys.argv[2])

    runJoern("/home/joern/Bookinfo/ratings/","ratings")