#!/bin/bash

# AFTER ISTIO IS INSTALLED AND NAMESPACE LABELED

kubectl create secret generic opa-policy --from-file=allow-policy.rego
kubectl apply -f opa.yaml
kubectl apply -f frontend.yaml
kubectl apply -f checkout.yaml
kubectl apply -f payment.yaml
kubectl apply -f cart.yaml
kubectl apply -f opaAuthz.yaml
kubectl apply -f envFilter.yaml
