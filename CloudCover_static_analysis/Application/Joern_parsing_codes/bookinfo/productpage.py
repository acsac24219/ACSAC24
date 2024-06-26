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

    query='cpg.call.name("<operator>.fieldAccess").code("requests.get").toJson'
    result=tool.formatJoernResult(tool.joern_client.execute(query))

    for item in result:
        method_query='cpg.call.id(%s).method.toJson'%(item['id'])
        method_result=tool.formatJoernResult(tool.joern_client.execute(method_query))[0]
        # pprint(method_result)

        # find url in request.get
        new_var_query='cpg.call.id(%s).astParent.astChildren.order(2).toJson'%(item['id'])
        new_var_result=tool.formatJoernResult(tool.joern_client.execute(new_var_query))[0]
        # pprint(new_var_result)

        # find url is assigned by other
        new_var_query_2='cpg.method.fullNameExact("%s").ast.isCall.name("<operator>.assignment").lineNumberLt(%s).where(_.astChildren.isIdentifier.name("%s")).ast.isCall.name("<operator>.indexAccess").ast.isIdentifier.name.dedup.toJson'%(method_result['fullName'],item['lineNumber'],new_var_result['name'])
        new_var_result_2=tool.formatJoernResult(tool.joern_client.execute(new_var_query_2))[0]


        # find details in global domain
        new_var_query_3='cpg.method.fullNameExact("productpage.py:<module>").astChildren.isBlock.astChildren.isCall.name("<operator>.assignment").code("%s .*").ast.isLiteral.toJson'%(new_var_result_2)
        new_var_result_3=tool.formatJoernResult(tool.joern_client.execute(new_var_query_3))

        global_var_value_dict[new_var_result_2]={
            new_var_result_3[0]['code']:new_var_result_3[1]['code'][1:-1],
            new_var_result_3[2]['code']:new_var_result_3[3]['code'][1:-1],
            new_var_result_3[4]['code']:'',
        }

        # find outtest layer of var, combine data layer by layer
        
        '''
        # cannot parse the result from joern
        new_var_query_2_depend='cpg.method.fullNameExact("%s").ast.isCall.name("<operator>.assignment").lineNumberLt(%s).where(_.astChildren.isIdentifier.name("%s")).ast.isCall.name("<operator>.indexAccess").ast.isLiteral.code.dedup.toJson'%(method_result['fullName'],item['lineNumber'],new_var_result['name'])
        new_var_result_2_depend=tool.formatJoernResult(tool.joern_client.execute(new_var_query_2_depend))
        '''

        method_url_dict[method_result['name']]=new_var_result_3[1]['code'][1:-1] + "/" + new_var_result_3[3]['code'][1:-1] + "/" + "*"

        # pprint(global_var_value_dict)
    # pprint(method_url_dict)

    final_result={}
    for name in method_url_dict:
        out_request=method_url_dict[name]
        parent_method_query='cpg.call.code("%s.*").order(2).method.name.toJson'%(name)
        parent_method_result=tool.formatJoernResult(tool.joern_client.execute(parent_method_query))
        

        for parent_name in parent_method_result:
            incoming_request_query='cpg.call.code("%s = app.route.*").ast.isLiteral.code.toJson'%(parent_name)
            incoming_request_result=tool.formatJoernResultWithoutJson(tool.joern_client.execute(incoming_request_query))
            if incoming_request_result != "[]":
                incoming_request_result=incoming_request_result[4:-4]
                # print(name,parent_name,incoming_request_result)

                if incoming_request_result not in final_result:
                    final_result[incoming_request_result]=[]

                tmp={'entry': incoming_request_result, 'send_request': out_request, 'dependence': []}
                final_result[incoming_request_result].append(tmp)



    for item in final_result:
        for result in final_result[item]:
            print(result)



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

    runJoern("/home/joern/Bookinfo/productpage/","productpage")