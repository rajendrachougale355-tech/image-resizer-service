pipeline {
    agent any

    options { 
        skipDefaultCheckout() 
    }

    environment {
        DOCKER_HUB_USER  = "rajchouugale"
        IMAGE_NAME       = "image-resizer01"
        SERVER_IP        = "13.233.167.76"
        DOCKER_CREDS_ID  = "rajchouugale"
        SSH_CREDS_ID     = "aws-server-ssh-key"
    }

    stages {
        stage('1. Pull Code From GitHub') {
            steps {
                echo 'Pulling the latest application updates from GitHub...'
                checkout scm
            }
        }

        stage('2. Build Docker Image') {
            steps {
                echo "Building the Docker image: ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"
                sh "docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest ."
            }
        }

        stage('3. Push Image to Docker Hub') {
            steps {
                echo 'Logging into Docker Hub and pushing the new image layer...'
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDS_ID}", usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh "echo ${PASS} | docker login -u ${USER} --password-stdin"
                    sh "docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"
                }
            }
        }

        stage('4. Deploy to AWS EC2') {
            steps {
                echo "Connecting via SSH to AWS Server at ${SERVER_IP}..."
                sshagent(["${SSH_CREDS_ID}"]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ubuntu@${SERVER_IP} '
                        echo "Successfully logged into AWS EC2 server!"
                        docker pull ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest
                        
                        docker stop ${IMAGE_NAME} || true
                        docker rm ${IMAGE_NAME} || true
                        
                        echo "Executing the microservice in background detached mode on port 80..."
                        docker run -d -p 80:5000 --name ${IMAGE_NAME} --restart unless-stopped ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest
                    '
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Automated pipeline execution completed successfully! Your application is live.'
        }
        failure {
            echo 'Pipeline execution encountered an error. Check the console logs above to debug.'
        }
    }
}
