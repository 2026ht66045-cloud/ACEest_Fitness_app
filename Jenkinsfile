pipeline {
    agent any

    environment {
        IMAGE_NAME = "aceest-fitness"
        REGISTRY = "your-docker-registry" // Optional: leave blank for local docker
    }

    stages {
        stage('Checkout & Validate') {
            steps {
                // 1. Run Python syntax check
                sh 'python3 validate_code.py'
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
            echo "Build or Deployment failed! Rolling back to previous stable version..."
            script {
                // Stop the broken container
                sh 'docker stop aceest-app || true'
                sh 'docker rm aceest-app || true'

                // Rollback: Spin up the last known 'stable' container
                sh 'docker run -d --name aceest-app ${IMAGE_NAME}:stable'
            }
            echo "Rollback complete. System reverted to 'stable'."
        }
    }
}