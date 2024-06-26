#!/bin/bash

kubectl apply -f metallb/
sleep 60
OPA-Testing/istio-1.16.0/bin/istioctl install --set profile=OPA-Testing/istio-1.16.0/manifests/profiles/default.yaml -y
sleep 5
kubectl label namespace default istio-injection=enabled
