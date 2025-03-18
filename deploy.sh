#!/bin/bash

$EMAIL="aky8507049610@gmail.com"
SERVER_IP="20.244.3.129"
SERVER_USER="your_vm_username"
SERVER_PASSWORD="your_vm_server_password"
GIT_USERNAME="AbhyArya"
GIT_USER="your_github_token_or_user_name"
GIT_PASSWORD="your_github_token"
REPO_NAME="backend"
GIT_URL="https://$GIT_USER:$GIT_PASSWORD@github.com/$GIT_USERNAME/$REPO_NAME.git"

deploy_admin() {
    echo "Backend Deployement started"
    echo "===================================="
    sshpass -p $SERVER_PASSWORD ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << EOF
      sudo su
      cd $REPO_NAME
      echo "Pulling latest code..."
      git pull $GIT_URL
      echo "Building and deploying"
      docker compose up --build -d
      if [ \$? -eq 0 ]; then
        echo "Deployment succeeded."
      else
        echo "Deployment failed."
      fi
EOF
    echo "===================================="
}


deploy_admin
