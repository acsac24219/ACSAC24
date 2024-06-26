#!/bin/bash

# AFTER ISTIO IS INSTALLED AND NAMESPACE LABELED

kubectl apply -f frontend.yaml
kubectl apply -f checkout.yaml
kubectl apply -f payment.yaml
kubectl apply -f cart.yaml
