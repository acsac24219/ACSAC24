# CloudCover Artifacts



## Directory introduction
* **Application** -- it is the source codes of Bookinfo, Online Boutique, SockShop. Joern_parsing_codes is directory of python codes parsing three applications
* **DeathStarBench** -- it is the source codes of mediaMicroservice and socialNetwork
* **Dockerfile** -- it is the docker build file



## Installation and usage
We use docker to run Joern and all commands should be ran under the directory paper_artifacts
### 1 installation

```shell
cd paper_artifacts
docker build -t 'joern:v2.0.232' .
```

### 2 run container
```shell
docker run -it -v `pwd`:/home 'joern:v2.0.232' /bin/bash
```

### 3 run Joern to parse DeathStarBench
```shell
cd DeathStarBench/socialNetwork
joern --script get_dependency_graph_file_base_socialNetwork.sc --param cpgFile=workspace/cpg.bin/cpg.bin --param outFile=result.json

# generate dependency graph and call chain after Joern parsing
python print_dependency_graph_file_base.py
python generate_call_chain.py



cd DeathStarBench/mediaMicroservice
joern --script get_dependency_graph_file_base_mediaMicroservices.sc --param cpgFile=workspace/cpg.bin/cpg.bin --param outFile=result.json
python print_dependency_graph_file_base.py
python generate_call_chain.py




```


