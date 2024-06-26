#!/bin/bash

kubectl delete -f ../opa.yaml
kubectl delete -f ext-service.yaml
kubectl delete -f fake-service1.yaml
kubectl delete -f fake-service2.yaml
kubectl delete -f fake-service3.yaml
kubectl delete -f fake-service4.yaml
kubectl delete -f fake-service5.yaml
kubectl delete -f etcd.yaml
kubectl delete -f opaAuthz.yaml
kubectl delete -f envFilter.yaml

