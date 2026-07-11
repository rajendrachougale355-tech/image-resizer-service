pipeline {
    agent any

    environment {
        
        DOCKER_HUB_USER  = "rajchouugale"
        IMAGE_NAME       = "image-resizer"
        SERVER_IP        = "65.0.185.32"
        
       
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
                        
                        # Pull down the latest image you just pushed to Docker Hub
                        docker pull ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest
                        
                        # Stop and remove the old running container if it exists, so ports don't clash
                        docker stop ${IMAGE_NAME} || true
                        docker rm ${IMAGE_NAME} || true
                        
                        # Run the newly updated image resizer container
                        echo "Executing the microservice in the cloud environment..."
                        docker run --name ${IMAGE_NAME} --rm ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest
                    '
                    """
                }
            }
        }
    }

    post {
        success {
            echo ' Automated pipeline execution completed successfully! Your application is live.'
        }
        failure {
            echo ' Pipeline execution encountered an error. Check the console logs above to debug.'
        }
    }
}
