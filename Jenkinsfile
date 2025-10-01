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
               echo "Building and pushing image to Docker Hub..."

                // Build production image
                bat 'docker build -t myapp:prod .'

                // Tag the image with your Docker Hub repo
                bat 'docker tag myapp:prod omarnoman/myapp:latest'

                // Login to Docker Hub using Jenkins credentials
                withCredentials([string(credentialsId: 'dockerhub-credentials', variable: 'DOCKER_TOKEN')]) {
                    bat 'docker login -u omarnoman -p %DOCKER_TOKEN%'
                }

                // Push image to Docker Hub
                bat 'docker push omarnoman/myapp:latest'

                echo "Image successfully pushed to Docker Hub!"
                
            }
        }

        stage('Monitoring') {
            steps {
                echo 'Monitoring stage'
                bat '''
                docker run -d --name dd-agent \
                -e DD_API_KEY=datadog_api \
                -e DD_SITE="ap2.datadoghq.com" \
                -e DD_DOGSTATSD_NON_LOCAL_TRAFFIC=true \
                -v /var/run/docker.sock:/var/run/docker.sock:ro \
                -v /proc/:/host/proc/:ro \
                -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
                -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
                gcr.io/datadoghq/agent:7
                '''
                echo "Datadog has started monitoring"

            }
        }
    }
}


































