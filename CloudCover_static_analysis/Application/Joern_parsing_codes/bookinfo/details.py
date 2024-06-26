import json
import sys
import re
import queue
from pprint import pprint
from collections import OrderedDict
from urllib.parse import urlparse
from cpgqls_client import CPGQLSClient, import_code_query, workspace_query
import time


import tool




def getDataFlow():

    query='cpg.call.name("request").argument.argumentIndex(1).reachableByFlows(cpg.identifier).dedup.toJson'
    result=tool.formatJoernResultV2(tool.joern_client.execute(query))


    var_dict={}
    send_request_url=''
    condition_list=[]
    line_number_set=set()
    for item in result[15]['elements']:
        if item['lineNumber'] in line_number_set:
            continue

        # pprint(item)
        line_number_set.add(item['lineNumber'])
        if item['_label'] == 'IDENTIFIER':
            tmp_query='cpg.call.lineNumber(%s).name("<operator>.assignment").argument.toJson'%(item['lineNumber'])
            tmp_result=tool.formatJoernResultV2(tool.joern_client.execute(tmp_query))
            # pprint(item)
            # pprint(tmp_result)
            if tmp_result and tmp_result[1]['_label'] == 'LITERAL':
                var_dict[tmp_result[0]['name']]=tmp_result[1]['code']
                # pprint(var_dict)
            elif tmp_result and tmp_result[1]['_label'] == 'CALL':
                second_query='cpg.call.id(%s).ast.toJson'%(tmp_result[1]['id'])
                second_result=tool.formatJoernResultV2(tool.joern_client.execute(second_query))
                if second_result[-3]['_label']=='CALL' and second_result[-3]['name']=='<operator>.addition':
                    v1=second_result[-2]['code'] if second_result[-2]['_label'] == 'LITERAL' else var_dict.get(second_result[-2]['name'],'')
                    v2=second_result[-1]['code'] if second_result[-1]['_label'] == 'LITERAL' else var_dict.get(second_result[-1]['name'],'')

                    var_dict[tmp_result[0]['name']]=v1+v2
                    send_request_url=v1+v2
        elif item['_label'] == 'METHOD_PARAMETER_IN':
            tmp_query='cpg.parameter.id(%s).method.name.toJson'%(item['id'])
            tmp_result=tool.formatJoernResultV2(tool.joern_client.execute(tmp_query))
            control_query='cpg.call.name("%s").controlledBy.code.toJson'%(tmp_result[0])
            control_result=tool.formatJoernResultV2(tool.joern_client.execute(control_query))
            condition_list.append(control_result[0])

    annotation_query='cpg.call.name("mount_proc").toJson'
    annotation_result=tool.formatJoernResultV2(tool.joern_client.execute(annotation_query))

    annotation_value_query='cpg.literal.lineNumber(%s).toJson'%(annotation_result[1]['lineNumber'])
    annotation_value_result=tool.formatJoernResultV2(tool.joern_client.execute(annotation_value_query))


    final_result={
                    'entry':annotation_value_result[0]['code'],
                    'send_request':send_request_url,
                    'dependence':[],
                    'condition':condition_list
                }
    pprint(final_result)

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
    print("parse time:%f"%(time.time()-start))

if __name__ == '__main__':
    # if 3!=len(sys.argv):
    #     print("Usage: python3 parse_multi_hop.py <inputPath> <projectName>")
    #     exit(-1)
    # runJoern(sys.argv[1],sys.argv[2])

    runJoern("/home/joern/Bookinfo/details/","details")