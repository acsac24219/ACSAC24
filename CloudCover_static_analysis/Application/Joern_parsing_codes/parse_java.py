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

REQUEST_TYPE_HTTP='HTTP'
REQUEST_TYPE_TCP='TCP'
REQUEST_TYPE_ANNOTATION='ANNOTATION'
#{'HTTP': [api1,api2], 'TCP': [api3], 'ANNOTATION':[]}
request_api={
    REQUEST_TYPE_HTTP:[],
    REQUEST_TYPE_TCP:[],
    REQUEST_TYPE_ANNOTATION:[],
}

cpg_dict={}

def getDataFlow():
    global request_api
    global cpg_dict
    service_api={}
    service_api_dependence={}
    annotation_list=[]


    # check annotation
    for annotation_name in request_api[REQUEST_TYPE_ANNOTATION]:
        annotation_query='cpg.annotation.name("%s").dedup.toJson'%(annotation_name)
        result=tool.formatJoernResult(tool.joern_client.execute(annotation_query))
        for annotation in result:
            service_api[annotation['code']]=set()
            service_api_dependence[annotation['code']]={}
            cpg_dict[annotation['id']]=annotation
        annotation_list.extend(result)



    # check the original request
    for request_type in request_api:
        if request_type == REQUEST_TYPE_ANNOTATION:
            continue
        for request_name in request_api[request_type]:
            for annotation in annotation_list:
                query_tcp='cpg.method.where(_.annotation.id(%d)).ast.isCall.methodFullName("%s.*").dedup.toJson'%(annotation['id'],request_name)
                result_tcp = tool.formatJoernResult(tool.joern_client.execute(query_tcp))
                for item in result_tcp:
                    item['request_type']=request_type
                    cpg_dict[item['id']]=item
                    service_api[annotation['code']].add(item['id'])



    # check the parent request of original request
    for request_type in request_api:
        if request_type == REQUEST_TYPE_ANNOTATION:
            continue
        for request_name in request_api[request_type]:
            method_of_request='cpg.call.methodFullName("%s.*").method.dedup.toJson'%(request_name)
            method_list = tool.formatJoernResult(tool.joern_client.execute(method_of_request))
            for method in method_list:
                method['request_type']=request_type
                cpg_dict[method['id']]=method
                for annotation in annotation_list:
                    query_http='cpg.method.where(_.annotation.id(%d)).ast.isCall.name("%s").dedup.toJson'%(annotation['id'],method['name'])
                    result_http = tool.formatJoernResult(tool.joern_client.execute(query_http))
                    for item in result_http:
                        item['request_type']=request_type
                        cpg_dict[item['id']]=item
                        service_api[annotation['code']].add(item['id'])

    # pprint(service_api)

    # explore relation about different requests
    for in_api in service_api:
        call_id_set=service_api[in_api]
        call_id_list=list(call_id_set)
        for sink in call_id_set:
            for source in call_id_list:
                if sink != source and cpg_dict[source]['lineNumber'] < cpg_dict[sink]['lineNumber']:
                    # try data flow
                    query='cpg.call.id(%s).reachableByFlows(cpg.call.id(%s)).size'%(sink,source)
                    result=tool.formatJoernResultBySize(tool.joern_client.execute(query))
                    if result >= 1:
                        if sink not in service_api_dependence[in_api]:
                            service_api_dependence[in_api][sink]=[]
                        service_api_dependence[in_api][sink].append(source)
                    else:
                        # try control flow
                        query='cpg.call.id(%s).controlledBy.isCall.dedup.toJson'%(sink)
                        controlled_call=tool.formatJoernResult(tool.joern_client.execute(query))
                        for item in controlled_call:
                            if cpg_dict[source]['lineNumber'] < item['lineNumber']:
                                query='cpg.call.id(%s).reachableByFlows(cpg.call.id(%s)).size'%(item['id'],source)
                                result=tool.formatJoernResultBySize(tool.joern_client.execute(query))
                                if result >= 1:
                                    if sink not in service_api_dependence[in_api]:
                                        service_api_dependence[in_api][sink]=[]
                                    service_api_dependence[in_api][sink].append(source)

    # pprint(service_api_dependence)

    for in_api in service_api:
        extracted_request={
            'in_api':in_api,
        }
        for call_id in service_api[in_api]:
            extracted_request['out_request']=call_id
            extracted_request['type']=cpg_dict[call_id]['request_type']

            if call_id in service_api_dependence[in_api]:
                #sort the dependence
                dependence=service_api_dependence[in_api][call_id]
                dependence_line={}
                for i in dependence:
                    dependence_line[i]=cpg_dict[i]['lineNumber']

                sort_dependence_line=sorted(dependence_line.items(), key=lambda x: x[1])

                sort_dependence=[]
                for item in sort_dependence_line:
                    call_id,line_number=item
                    sort_dependence.append(call_id)

                extracted_request['dependence']=sort_dependence
            else:
                extracted_request['dependence']=[]

            print(extracted_request)



def openProject(inputPath,projectName):
    # query = import_code_query(inputPath,projectName)
    query = 'time{importCode(inputPath="%s", projectName="%s")}'%(inputPath,projectName)
    result = tool.joern_client.execute(query)
    # pprint(result)

    query="time{run.ossdataflow}"
    result = tool.joern_client.execute(query)
    # pprint(result)


def getAppConfigFile():
    configFile = tool.formatJoernResult(tool.joern_client.execute("cpg.configFile.toJson"))
    if configFile:

        appConfigFile = Properties()
        appConfigFile.load(configFile[0]['content'],"utf-8")

        # for k in appConfigFile:
        #     print(k,appConfigFile[k].data)


def getRequestAPIConf(request_api_conf_name='./request_api_java.conf'):
    global request_api
    with open(request_api_conf_name, 'r') as request_api_file:
        file_content=request_api_file.read()
        request_api=eval(file_content)

    # pprint(request_api)


def runJoern(inputPath,projectName):

    getRequestAPIConf()

    openProject(inputPath,projectName)

    getAppConfigFile()

    #todo get needed var (program slicing)
    start=time.time()
    getDataFlow()
    print("parse time:%f"%(time.time()-start))

if __name__ == '__main__':
    if 3!=len(sys.argv):
        print("Usage: python3 parse_multi_hop.py <inputPath> <projectName>")
        exit(-1)
    runJoern(sys.argv[1],sys.argv[2])

    # inputPath="/home/joern/Sock_Shop/orders/src/main"
    # projectName="orders"
    # runJoern(inputPath,projectName)
