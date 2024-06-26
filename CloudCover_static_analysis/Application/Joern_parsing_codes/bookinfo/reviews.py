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
    query='cpg.call.methodFullNameExact("javax.ws.rs.client.Client.target:javax.ws.rs.client.WebTarget(java.lang.String)").reachableByFlows(cpg.method.where(_.annotation.name("Path")).parameter).dedup.toJson'
    flows_path = tool.formatJoernResult(tool.joern_client.execute(query))


    final_call_chain=[]

    first_line_chain=OrderedDict()#{lineNumber:element}
    for flows in flows_path:
        elements=flows['elements']
        function_parameter_name=None
        for element in elements:
            dynamicTypeHintFullName=element.get("dynamicTypeHintFullName",None)
            name=element.get("name",None)
            evaluationStrategy=element.get("evaluationStrategy",None)
            isVariadic=element.get("isVariadic",None)
            code=element.get("code",None)
            typeFullName=element.get("typeFullName",None)
            columnNumber=element.get("columnNumber",None)
            order=element.get("order",None)
            _label=element.get("_label",None)
            index=element.get("index",None)
            argumentIndex=element.get("argumentIndex",None)
            lineNumber=element.get("lineNumber",None)
            element_id=element.get("id",None)
            signature=element.get("signature",None)
            methodFullName=element.get("methodFullName",None)

            if tool.LABEL_METHOD_PARAMETER_IN == _label:
                function_parameter_name=name
            elif tool.LABEL_CALL == _label:
                tool.analyzeCall(element_id,lineNumber)


def openProject(inputPath,projectName):
    # query = import_code_query(inputPath,projectName)
    query = 'importCode(inputPath="%s", projectName="%s")'%(inputPath,projectName)
    result = tool.joern_client.execute(query)

    query="run.ossdataflow"
    result = tool.joern_client.execute(query)


def getNeededData():
    query='cpg.call.methodFullNameExact("javax.ws.rs.client.Client.target:javax.ws.rs.client.WebTarget(java.lang.String)").astChildren.toJson'
    astChildren = tool.formatJoernResult(tool.joern_client.execute(query))
    for children in astChildren:
        if tool.LABEL_CALL == children['_label']:
            url=tool.call_value_dict.get(children['id'],None)
            if url is not None:
                # result={"type":"HTTP","method":"GET","send_request":"","path":"","api":"/reviews/{productId}"}
                result={"entry":"/reviews/{product_id}", "send_request":url,"dependence":[]}
                # url_parse=urlparse(url)
                # result['path']=url_parse.path
                print(result)

def getAllAnnotation():
    # print("\ngetAllAnnotation")
    dot_pattern=r'@Path\("(.*)"\)'
    dot_prog = re.compile(dot_pattern)
    api=[]
    query='cpg.annotation.name("Path").toJson'
    annotation_list = tool.formatJoernResult(tool.joern_client.execute(query))
    for annotation in annotation_list:
        code=annotation['code']
        result=dot_prog.match(code)
        if result:
            api.append(result.group(1))

    # pprint(api)

def runJoern(inputPath,projectName):
    openProject(inputPath,projectName)

    #todo get needed var (program slicing)
    start=time.time()
    tool.getMemberVar()
    getDataFlow()
    getNeededData()
    # getAllAnnotation()
    # print("parse time:%f"%(time.time()-start))


if __name__ == '__main__':
    # if 3!=len(sys.argv):
    #     print("Usage: python3 csr.py <inputPath> <projectName>")
    #     exit(-1)
    # runJoern(sys.argv[1],sys.argv[2])

    inputPath="/home/joern/Bookinfo/reviews/"
    projectName="reviews"
    runJoern(inputPath,projectName)
