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
                script {
                    def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                    withCredentials([string(credentialsId: 'jenkins-sonar', variable: 'SONAR_TOKEN')]) {
                        withSonarQubeEnv('SonarQube-Local') {
                            bat "${scannerHome}\\bin\\sonar-scanner.bat " +
                                "-Dsonar.projectKey=myapp " +
                                "-Dsonar.sources=. " +
                                "-Dsonar.login=%SONAR_TOKEN%"
                    }
                }
            }
        }
    }

        stage('Security') {
            steps {
                echo 'Security stage '
                bat 'docker run --rm -v %CD%:/app myapp:latest bandit -r /app -lll -x /app/venv'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploy stage'
                // Remove any existing container
                bat 'docker rm -f myapp-test || echo No container to remove'
                

                // Start the app
                bat 'docker-compose -f docker-compose.yml up -d'

        
            }
        }

        stage('Release') {
            steps {
                echo 'Release stage'
                // stop and remove the old production container
                bat 'docker stop myapp-prod || echo No container running'
                bat 'docker rm -f myapp-prod || echo No container to remove'

                //Build the new image
                bat 'docker build -t myapp:latest .'

                //run the container
                bat 'docker run -d --name myapp-prod -p 5001:500 myapp:latest'

                echo 'Production deployment complete'
                
            }
        }

        stage('Monitoring') {
            steps {
                echo 'Monitoring stage - placeholder'
            }
        }
    }
}



























