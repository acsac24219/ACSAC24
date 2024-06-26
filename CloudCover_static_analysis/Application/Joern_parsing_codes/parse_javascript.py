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
config_dict={}


def getDataFlow():
    global request_api
    global cpg_dict
    global config_dict
    final_result={}


    # check annotation
    for annotation_name in request_api[REQUEST_TYPE_ANNOTATION]:
        method_query='cpg.call.code(".*%s.*").ast.dedup.isMethodRef.toJson'%(annotation_name)
        result_method=tool.formatJoernResult(tool.joern_client.execute(method_query))

        for method_ref in result_method:
            for request_type in request_api:
                call_id_set=set()
                call_dependence={}
                call_url_dict={}
                if request_type == REQUEST_TYPE_ANNOTATION:
                    continue
                for request_name in request_api[request_type]:
                    # Find out all cases of out-request APIs
                    call_query='cpg.method.fullNameExact("%s").ast.isCall.name("%s").map(x=>(x.id,x.lineNumber)).toJson'%(method_ref['methodFullName'],request_name)
                    call_result=tool.formatJoernResult(tool.joern_client.execute(call_query))
                    for item in call_result:
                        call_id=item['_1']
                        lineNumber=item['_2']
                        cpg_dict[call_id]={'id':call_id,'lineNumber':lineNumber}
                        call_id_set.add(call_id)

                        # Find out the values of all variables in tainted function calls
                        # simple way to get these values
                        #var_query='cpg.call.id(%s).ast.isIdentifier.argumentIndex(1).toJson'%(call_id)
                        #argument_var=tool.formatJoernResult(tool.joern_client.execute(var_query))[-1]['name']

                        #literal_query='cpg.method.fullNameExact("%s").ast.isCall.name("<operator>.assignment").code(".*%s.*").whereNot(_.id(%s)).ast.isLiteral.dedup.toJson'%(method_ref['methodFullName'],argument_var,call_id)
                        #tool.joern_client.execute(literal_query)
                        # literal_result=tool.formatJoernResult(tool.joern_client.execute(literal_query))
                        # tmp_url=''
                        # for i in literal_result:
                        #     tmp_url=tmp_url+i['code'][1:-1]
                        # call_url_dict[call_id]=tmp_url

                # Analyze the relationship among these tainted function calls
                call_id_list=list(call_id_set)
                for sink in call_id_set:
                    for source in call_id_list:
                        if sink != source and cpg_dict[source]['lineNumber'] < cpg_dict[sink]['lineNumber']:
                            # try data flow
                            query='cpg.call.id(%s).reachableByFlows(cpg.call.id(%s).astChildren.isIdentifier).size'%(sink,source)
                            flows_path=tool.formatJoernResultBySize(tool.joern_client.execute(query))
                            if flows_path >= 1:
                                if sink not in call_dependence:
                                    call_dependence[sink]=set()
                                call_dependence[sink].add(source)
                            else:
                                # try control flow
                                query='cpg.call.id(%s).controlledBy.reachableByFlows(cpg.call.id(%s).astChildren.isIdentifier).size'%(sink,source)
                                control_flows_path=tool.formatJoernResultBySize(tool.joern_client.execute(query))
                                if control_flows_path >= 1:
                                    if sink not in call_dependence:
                                        call_dependence[sink]=set()
                                    call_dependence[sink].add(source)

                tmp_list=[]
                for call_id in call_id_set:
                    extracted_request={}
                    extracted_request['url']=call_url_dict.get(call_id,call_id)
                    # extracted_request['type']=request_type

                    if call_id in call_dependence:
                        #sort the dependence
                        dependence=call_dependence[call_id]
                        dependence_line={}
                        for i in dependence:
                            dependence_line[i]=cpg_dict[i]['lineNumber']

                        sort_dependence_line=sorted(dependence_line.items(), key=lambda x: x[1])

                        sort_dependence=[]
                        for item in sort_dependence_line:
                            call_id,line_number=item
                            sort_dependence.append(call_url_dict.get(call_id,call_id))

                        extracted_request['dependence']=sort_dependence
                    else:
                        extracted_request['dependence']=[]

                    tmp_list.append(extracted_request)

                if tmp_list:
                    pprint(tmp_list)
                    final_url=config_dict.get('server.ip','')
                    final_result[final_url]=tmp_list



        # pprint(final_result)


def openProject(inputPath,projectName):
    # query = import_code_query(inputPath,projectName)
    query = 'time{importCode(inputPath="%s", projectName="%s")}'%(inputPath,projectName)
    result = tool.joern_client.execute(query)
    # pprint(result)

    query="time{run.ossdataflow}"
    result = tool.joern_client.execute(query)
    # pprint(result)

def getAppConfigFile():
    global config_dict
    configFile = tool.formatJoernResult(tool.joern_client.execute("cpg.configFile.toJson"))
    if configFile:

        appConfigFile = Properties()
        appConfigFile.load(configFile[0]['content'],"utf-8")

        for k in appConfigFile:
            config_dict[k]=appConfigFile[k].data
            # print(k,appConfigFile[k].data)



def getRequestAPIConf(request_api_conf_name='./request_api_javascript.conf'):
    global request_api
    with open(request_api_conf_name, 'r') as request_api_file:
        file_content=request_api_file.read()
        request_api=eval(file_content)


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