pipeline {
    agent any

    environment {
        IMAGE_NAME = "aceest-fitness"
        STABLE_IMAGE_ID = "164438f9ae21"
    }

    stages {
        stage('Checkout & Validate') {
            steps{
                echo 'Checking out main branch'
                checkout scm
            }
        }

        stage('Build New Docker Image') {
            steps {
                // Build the new image with a unique build tag and 'latest'
                script {
                    dockerImage = docker.build("${IMAGE_NAME}:${env.BUILD_NUMBER}")
                    dockerImage.tag("latest")
                }
            }
        }

        stage('Test & Deploy') {
            steps {
                script {
                    try {
                        // Stop old container if running
                        sh 'docker stop aceest-app || true'
                        sh 'docker rm aceest-app || true'

                        // Run the new container
                        sh 'docker run -d --name aceest-app ${IMAGE_NAME}:latest'

                        // Run integration/smoke tests here
                        // sh 'pytest test_app.py'

                        // If tests pass, promote current 'latest' to be the new 'stable'
                        sh 'docker tag ${IMAGE_NAME}:${env.BUILD_NUMBER} ${IMAGE_NAME}:stable'
                        
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error("Deployment failed, triggering rollback...")
                    }
                }
            }
        }
    }

    post {
    failure {
        echo "Build failed! Rolling back to stable image ID: ${STABLE_IMAGE_ID}..."
        script {
            try {
                // Prepend sudo to docker commands
                sh 'sudo docker stop aceest-app || true'
                sh 'sudo docker rm aceest-app || true'
                sh 'sudo docker run -d --name aceest-app ${STABLE_IMAGE_ID}'
                echo "Rollback complete using image ID ${STABLE_IMAGE_ID}."
            } catch (Exception err) {
                echo "Rollback encountered an error: ${err.getMessage()}"
            }
        }
    }
}
}