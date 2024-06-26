#!/bin/bash

# AFTER ISTIO IS INSTALLED AND NAMESPACE LABELED

kubectl create secret generic opa-policy --from-file=allow-all.rego
kubectl apply -f opa-allow-monitor.yaml
kubectl apply -f gcp.yaml
#kubectl apply -f etcd.yaml
kubectl apply -f opaAuthz.yaml
#kubectl apply -f envFilter.yaml

