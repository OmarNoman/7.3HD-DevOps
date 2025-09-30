pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Build stage'
                bat 'docker build -t myapp:latest .'
            }
        }

        stage('Test') {
            steps {
                echo 'Test stage'
                bat 'docker run --rm myapp:latest pytest -v'
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Code Quality stage'
                withSonarQubeEnv('Local SonarQube') {
                bat 'sonar-scanner -Dsonar.projectKey=myapp -Dsonar.sources=.'
            }
        }

        stage('Security') {
            steps {
                echo 'Security stage - placeholder'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploy stage - placeholder'
            }
        }

        stage('Release') {
            steps {
                echo 'Release stage - placeholder'
            }
        }

        stage('Monitoring') {
            steps {
                echo 'Monitoring stage - placeholder'
            }
        }
    }
}








