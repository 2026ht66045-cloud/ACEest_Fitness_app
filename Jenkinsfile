pipeline {
    agent any
    triggers {
        githubPush()
    }

    environment {
        // Replace with your Docker Hub username and repository name
        DOCKER_IMAGE = "2026ht66045/aceest_app"
        // Uses Jenkins build number as the image tag
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out main branch'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Installing python dependencies'
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running Automated Test'
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install --no-cache-dir -r requirements.txt
                    .venv/bin/pip install pytest pytest-xvfb matplotlib
                    .venv/bin/pytest tests/
                '''
            }
        }

        stage('Docker Build & Push') {
            steps {
                echo 'Building and pushing Docker image to Docker Hub'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker build -t $DOCKER_IMAGE:$IMAGE_TAG -t $DOCKER_IMAGE:latest .
                        docker push $DOCKER_IMAGE:$IMAGE_TAG
                        docker push $DOCKER_IMAGE:latest
                        docker logout
                    '''
                }
            }
        }
    }

    post {
        always {
            // Clean up local images to save disk space on the Jenkins agent
            sh "docker rmi $DOCKER_IMAGE:$IMAGE_TAG $DOCKER_IMAGE:latest || true"
        }
    }
}