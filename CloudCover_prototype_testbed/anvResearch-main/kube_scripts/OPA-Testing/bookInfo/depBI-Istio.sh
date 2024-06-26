#!/bin/bash

# AFTER ISTIO IS INSTALLED AND NAMESPACE LABELED

kubectl apply -f bookinfo.yaml
kubectl apply -f bookInfoAuthzPolicy.yaml
