# Start Minikube
minikube start

# Check that Kubernetes has come up and pods are listed as "Running"
minikube kubectl -- get pods -A -o wide

# Install the fake-service files you've created
* Install the fake-serviceX.yaml files one-by-one using the following command
minikube kubectl -- apply -f <fileName here>

# Expose the Fake Service 1 so that you can reach it from your localhost
minikube service fs1 --url

# Use the URL exposed to curl the system
curl <URL from previous command>
