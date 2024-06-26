#!/bin/bash

# AFTER ISTIO IS INSTALLED AND NAMESPACE LABELED

kubectl create secret generic opa-policy --from-file=allow-policy.rego
kubectl apply -f ../opa.yaml
kubectl apply -f ext-service.yaml
kubectl apply -f fake-service1.yaml
kubectl apply -f fake-service2.yaml
kubectl apply -f fake-service3.yaml
kubectl apply -f fake-service4.yaml
kubectl apply -f fake-service5.yaml
kubectl apply -f etcd.yaml
kubectl apply -f opaAuthz.yaml
kubectl apply -f envFilter.yaml

