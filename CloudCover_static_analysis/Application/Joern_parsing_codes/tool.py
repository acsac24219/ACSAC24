from cpgqls_client import CPGQLSClient, import_code_query, workspace_query
import time
import json
import re
import queue
from pprint import pprint
from collections import OrderedDict
from urllib.parse import urlparse
from collections import deque

server_endpoint = "localhost:8080"
basic_auth_credentials = ("username", "password")
joern_client = CPGQLSClient(server_endpoint, auth_credentials=basic_auth_credentials)

pattern=r"^(res\d*: String = \")(.*)\"$"
prog = re.compile(pattern)

pattern_int=r"^(res\d*: Int = )(.*)$"
prog_int = re.compile(pattern_int)

dot_pattern=r'  "(\d+)" -> "(\d+)" '
dot_prog = re.compile(dot_pattern)

LABEL_IDENTIFIER="IDENTIFIER"
LABEL_METHOD_PARAMETER_IN="METHOD_PARAMETER_IN"
LABEL_CALL="CALL"
LABEL_LITERAL="LITERAL"



CONFIG={
    "ENABLE_RATINGS":'True',
    "SERVICES_DOMAIN":"bookinfo.com",
    "HOSTNAME":"reviews.bookinfo.com",
    "CLUSTER_NAME":"rest_test",
}

var_dict={}
call_dict={}
call_ast_dict={}
call_value_dict={}

def formatJoernResult(result):
    return json.loads(eval("'{}'".format(prog.match(result['stdout'].strip()).group(2))))

def formatJoernResultBySize(result):
    return json.loads(eval("'{}'".format(prog_int.match(result['stdout'].strip()).group(2))))

def getMemberVar():
    cpg_cmd='cpg.method.name("<clinit>").ast.isCall.argumentIndex(-1).id.dedup.toJson'
    call_ids=formatJoernResult(joern_client.execute(cpg_cmd))
    for call_id in call_ids:
        analyzeMemberVar(call_id)

def analyzeMemberVar(call_id):
    # print("analyzeMemberVar call_id:%d"%(call_id))
    cpg_cmd="cpg.call.id(%d).ast.isCall.dedup.toJson"%(call_id)
    call_list=formatJoernResult(joern_client.execute(cpg_cmd))
    for call in reversed(call_list):
        analyzeSubCall(call)

    # pprint(var_dict)

def getLocalVar(call_id,line_number):
    # print("getLocalVar call_id:%d line_number:%d"%(call_id,line_number))


    cpg_cmd="cpg.call.id(%d).method.toJson"%(call_id)
    method_element=formatJoernResult(joern_client.execute(cpg_cmd))[0]
    fullName=method_element['fullName']
    line_start=method_element['lineNumber']

    cpg_cmd="cpg.call.id(%d).ast.isIdentifier.dedup.name.toJson"%(call_id)
    line_identifier = formatJoernResult(joern_client.execute(cpg_cmd))

    cpg_cmd="cpg.call.id(%d).method.local.toJson"%(call_id)
    local_element=formatJoernResult(joern_client.execute(cpg_cmd))
    # pprint(local_element)

    local_cmd_stack = deque()
    local_identifier_stack = deque(line_identifier)

    while 0!=len(local_identifier_stack):
        local_identifier=local_identifier_stack.pop()

        for local_var in local_element:
            name=local_var['name']
            code=local_var['code']

            if name == local_identifier:
                #check new local var
                cpg_cmd='cpg.method.fullNameExact("%s").call.name("<operator>.assignment").lineNumberGte(%d).lineNumberLt(%d).code("%s.*").dedup.astChildren.isCall.ast.isIdentifier.name.toJson'%(fullName,line_start,line_number,code)
                new_local_identifiers=formatJoernResult(joern_client.execute(cpg_cmd))
                for new_local_identifier in new_local_identifiers:
                    local_identifier_stack.append(new_local_identifier)

                cpg_cmd='cpg.method.fullNameExact("%s").call.name("<operator>.assignment").lineNumberGte(%d).lineNumberLt(%d).code("%s.*").dedup.id.toJson'%(fullName,line_start,line_number,code)
                local_cmd_stack.append(cpg_cmd)

    while 0!=len(local_cmd_stack):
        cpg_cmd=local_cmd_stack.pop()
        # print(cpg_cmd)
        local_call_id=formatJoernResult(joern_client.execute(cpg_cmd))
        for element in local_call_id:
            analyzeLocalVarLine(element)


def analyzeLocalVarLine(call_id):
    # print("analyzeLocalVarLine call_id:%d"%(call_id))
    cpg_cmd="cpg.call.id(%d).ast.isCall.dedup.toJson"%(call_id)
    call_list=formatJoernResult(joern_client.execute(cpg_cmd))
    for call in reversed(call_list):
        analyzeSubCall(call)

    # pprint(var_dict)



def analyzeCall(call_id,line_number):
    # print("\nanalyzeCall call_id:%d"%(call_id))
    getLocalVar(call_id,line_number)
    cpg_cmd="cpg.call.id(%d).ast.isCall.dedup.toJson"%(call_id)
    call_list=formatJoernResult(joern_client.execute(cpg_cmd))
    for call in reversed(call_list):
        analyzeSubCall(call)

    
    # pprint(call_value_dict)
    # pprint(var_dict)

def analyzeSubCall(call):
    call_dict[call['id']]=call
    cpg_cmd="cpg.call.id(%d).astChildren.toJson"%(call['id'])
    astChildren=formatJoernResult(joern_client.execute(cpg_cmd))
    call_ast_dict[call['id']]=astChildren

    if "<operator>.addition" == call['methodFullName']:
        call_value_dict[call['id']]=""
        for children in astChildren:
            if LABEL_LITERAL == children['_label']:
                call_value_dict[call['id']]+=children['code'].strip('"')
            elif LABEL_CALL == children['_label']:
                call_value_dict[call['id']]+=call_value_dict[children['id']]
            elif LABEL_IDENTIFIER == children['_label']:
                call_value_dict[call['id']]+=var_dict.get(children['name'],children['name'])

    elif "<operator>.assignment" == call['methodFullName']:
        k=astChildren[0]['name']
        v_label=astChildren[1]['_label']
        if LABEL_LITERAL == v_label:
            v=astChildren[1]['code'].strip('"')
            var_dict[k]=v
        elif astChildren[1]['id'] in call_value_dict:
            v=call_value_dict[astChildren[1]['id']]
            var_dict[k]=v

    elif "<operator>.arrayInitializer" == call['methodFullName']:
        call_value_dict[call['id']]=[]
        for children in astChildren:
            if LABEL_LITERAL==children['_label'] and not children['code'].startswith("//"):
                call_value_dict[call['id']].append(children['code'].strip('"'))
            elif LABEL_CALL==children['_label']:
                call_value_dict[call['id']].append(call_value_dict.get(children['id'],[]))

    elif "<operator>.minus" == call['methodFullName']:
        call_value_dict[call['id']]="-"+astChildren[0]['code'] if LABEL_LITERAL==astChildren[0]['_label'] else ""

    elif '<operator>.equals' == call['methodFullName']:
        compare_a = call_value_dict[astChildren[0]['id']] if LABEL_CALL==astChildren[0]['_label'] else astChildren[0]['code'].strip('"')
        compare_b = call_value_dict[astChildren[1]['id']] if LABEL_CALL==astChildren[1]['_label'] else astChildren[1]['code'].strip('"')

        if 'null' == compare_b and compare_a is None:
            call_value_dict[call['id']]=True
        else:
            call_value_dict[call['id']]=False

    elif '<operator>.conditional' == call['methodFullName']:
        compare_result=call_value_dict[astChildren[0]['id']]
        result_a=call_value_dict[astChildren[1]['id']] if LABEL_CALL==astChildren[1]['_label'] else astChildren[1]['code'].strip('"')
        result_b=call_value_dict[astChildren[2]['id']] if LABEL_CALL==astChildren[2]['_label'] else astChildren[2]['code'].strip('"')

        if compare_result:
            call_value_dict[call['id']]=result_a
        else:
            call_value_dict[call['id']]=result_b


    elif '<operator>.fieldAccess' == call['methodFullName']:
        call_value_dict[call['id']]=var_dict.get(astChildren[1]['canonicalName'],None)


    elif 'java.lang.String.format:java.lang.String(java.lang.String,java.lang.Object[])' == call['methodFullName']:
        python_format_list=[]
        python_format_list.append(astChildren[1]['code'])
        python_format_list.append("%(")
        for arg in call_value_dict[astChildren[2]['id']]:
            python_format_list.append('"'+arg+'",')

        python_format_list[-1]=python_format_list[-1][:-1]
        python_format_list.append(")")
        python_format_str="".join(python_format_list)
        try:
            call_value_dict[call['id']]=eval(python_format_str)
        except:
            print("String.format error str:"+repr(python_format_str))

    elif 'java.lang.System.getenv:java.lang.String(java.lang.String)' == call['methodFullName']:
        env_var=astChildren[1]['code'].strip('"')
        call_value_dict[call['id']]=CONFIG.get(env_var,None)

    elif 'java.lang.Boolean.valueOf:java.lang.Boolean(java.lang.String)' == call['methodFullName']:
        call_value_dict[call['id']]=eval(call_value_dict[astChildren[1]['id']])


    else:
        pass
        # print('unknown methodFullName:'+call['methodFullName'])
        # pprint(call)

    
all_nodes_dict={}
def getAllNodes():
    all_nodes = formatJoernResult(joern_client.execute("cpg.all.toJson"))
    for node in all_nodes:
        all_nodes_dict[node['id']]=node

    # pprint(all_nodes_dict)


ast_dict={}
def getAllAst():
    # all_asts = formatJoernResult(joern_client.execute("cpg.method.dotAst.take(1).toJson"))
    # all_asts = formatJoernResult(joern_client.execute("cpg.method.dotAst.toJson"))
    all_asts = formatJoernResult(joern_client.execute("cpg.call.dotAst.toJson"))
    for node in all_asts:
        lines=node.split('\n')
        for line in lines:
            result=dot_prog.match(line)
            if result:
                parent=int(result.group(1))
                children=int(result.group(2))
                if parent not in ast_dict:
                    ast_dict[parent]=[]
                if children not in ast_dict[parent]:
                    ast_dict[parent].append(children)

    for parent in ast_dict:
        pprint(all_nodes_dict[parent])
        for children in ast_dict[parent]:
            pprint(all_nodes_dict[children])

        print("\n")


if __name__ == '__main__':
    query = import_code_query("/home/joern/rest/LibertyRestEndpoint.java", "reviews")
    result = joern_client.execute(query)
    # print(result['stdout'])

    query="run.ossdataflow"
    result = joern_client.execute(query)
    # print(result['stdout'])

    getAllNodes()
    getAllAst()
