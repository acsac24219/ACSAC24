#!/bin/bash

# AFTER ISTIO IS INSTALLED AND NAMESPACE LABELED

kubectl delete secret opa-policy
kubectl delete -f opa.yaml
kubectl delete -f frontend.yaml
kubectl delete -f checkout.yaml
kubectl delete -f payment.yaml
kubectl delete -f cart.yaml
kubectl delete -f opaAuthz.yaml
kubectl delete -f envFilter.yaml
