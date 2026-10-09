pipeline {
    agent any
    triggers{
     pollSCM('H/2 * * * *')
    }

    stages{
        stage('Checkout'){
            steps{
                echo 'Checking out main branch'
                checkout scm
            }
        }

        stage('Build'){
            steps{
                echo 'installing python dependencies'

                sh '''
                     python3 -m venv .venv
                     sudo dnf install -y python3-pip
                     .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Tesy'){
            steps{
                echo 'Running Automated Test'

                sh '''
                    pytest aceest_app.py
                '''
            }
        }
    }
}