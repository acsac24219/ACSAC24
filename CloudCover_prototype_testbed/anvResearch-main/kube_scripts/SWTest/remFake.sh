#!/bin/bash

# AFTER ISTIO IS INSTALLED AND NAMESPACE LABELED

kubectl delete -f frontend.yaml
kubectl delete -f checkout.yaml
kubectl delete -f payment.yaml
kubectl delete -f cart.yaml
