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
                // Stop any running container
                bat 'docker stop myapp-test || echo No running container'

                // Remove any existing container
                bat 'docker rm -f myapp-test || echo No container to remove'
                

                // Start the app
                bat 'docker-compose -f docker-compose.yml up -d'

                // Check container health
                script {
                    def status = bat(script: 'docker inspect --format="{{.State.Health.Status}}" myapp-test', returnStdout: true).trim()
                    if (status != "healthy") {
                        echo "Deployment failed, rolling back..."
                        // Rollback: start previous container (optional: use previous tag or backup)
                        bat 'docker-compose -f docker-compose.yml down'
                        error("Deployment failed: container unhealthy")
                    } else {
                        echo "Deployment successful, container is healthy."
            }
                
            }
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
























