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
                bat 'docker stop myapp-test || echo No running container to stop'
                bat 'docker rm myapp-test || echo No container to remove'

                bat 'docker run -d --name myapp-test -p 5000:5000 myapp:latest'
                bat 'docker ps -f name=myapp-test'

                
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




















