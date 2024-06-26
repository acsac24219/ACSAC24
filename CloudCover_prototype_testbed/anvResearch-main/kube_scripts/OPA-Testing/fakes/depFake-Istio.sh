#!/bin/bash

# AFTER ISTIO IS INSTALLED AND NAMESPACE LABELED

kubectl apply -f ext-service.yaml
kubectl apply -f fake-service1.yaml
kubectl apply -f fake-service2.yaml
kubectl apply -f fake-service3.yaml
kubectl apply -f fake-service4.yaml
kubectl apply -f fake-service5.yaml
kubectl apply -f istioAuthz.yaml

