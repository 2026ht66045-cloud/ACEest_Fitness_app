pipeline {
    triggers{
     pollSCM('H/2 * * * *')
    }

    stages{
        stage('Checkout'){
            steps{
                echo 'Checking out main branch'
            }
        }

        stage('Build'){
            steps{
                echo 'installing python dependencies'

                sh '''
                     python3 -m venv .venv
                     .venv/bin/pip install -r requirements.txt
                '''
            }
        }
    }
}