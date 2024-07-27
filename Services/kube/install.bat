@echo off
echo Installing necessary tools...
kubectl version --client
if %errorlevel% neq 0 (
    echo Kubectl is not installed. Please install Kubectl first.
    exit /b 1
)

echo Deleting existing Minikube cluster...
minikube delete

echo Clearing Minikube cache...
minikube cache delete

echo Starting Minikube with specific resources...
minikube start --cpus=max --memory=max --v=7 --alsologtostderr
if %errorlevel% neq 0 (
    echo Failed to start Minikube.
    exit /b 1
)

echo Enabling Ingress controller...
minikube addons enable ingress
if %errorlevel% neq 0 (
    echo Failed to enable Ingress controller.
    exit /b 1
)

echo Installation complete.
