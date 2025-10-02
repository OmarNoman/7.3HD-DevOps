pipeline {
    agent any
    environment {
        BUILDTAG = "${env.BUILD_NUMBER}"
    }
        

    stages {
        stage('Build') {
            steps {
                echo 'Build stage'
                bat """
                docker build -t omarnoman/python_login_webapp_webapp:${BUILDTAG} -t omarnoman/python_login_webapp:latest .
                 """
            }
        }

        stage('Test') {
            steps {
                echo 'Test stage'
                bat 'docker run --rm -v %CD%:/app omarnoman/python_login_webapp:latest pytest --cov=python_login_webapp --cov-report=term-missing --cov-report=xml:coverage.xml'

            }
        }

        stage('Code Quality') {
            steps {
                echo 'Code Quality stage'
                script {
                    def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                    withCredentials([string(credentialsId: 'jenkins-sonar', variable: 'SONAR_TOKEN')]) {
                        withSonarQubeEnv('SonarQube-Local') {
                            bat """
                                ${scannerHome}\\bin\\sonar-scanner.bat ^
                                -Dsonar.projectKey=python_login ^
                                -Dsonar.sources=python_login_webapp ^
                                -Dsonar.tests=tests ^
                                -Dsonar.python.version=3.11 ^
                                -Dsonar.python.coverage.reportPaths=coverage.xml ^
                                -Dsonar.token=%SONAR_TOKEN%
                            """
                        }      
                    }
                }
            }
        }


        stage('Security') {
            steps {
                echo 'Security stage '
                bat 'docker run --rm -e ENV=production -v %CD%:/app omarnoman/python_login_webapp:latest bandit -r /app -lll -x /app/venv'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploy stage'

                bat"""
                docker build -t omarnoman/python_login_webapp:latest .
                """

                // Remove any existing container
                bat 'docker stop python_login_webapp-test || echo No existing python_login_webapp container running'
                bat 'docker rm -f python_login_webapp-test || echo No existing python_login_webapp container to remove'
                
                
                // Run the container
                bat """
                docker run -d --name python_login_webapp-test ^
                    -e CI=true ^
                    -p 5000:5000 ^
                    omarnoman/python_login_webapp:latest
                """

                bat"""
                timeout /t 5
                docker ps -a
                """
            }
        }

        stage('Release') {
            steps {
               echo "Building and pushing image to Docker Hub..."

                // Build production image
                bat "docker build -t omarnoman/python_login_webapp:${BUILDTAG} -t omarnoman/python_login_webapp:latest ."

                withCredentials([string(credentialsId: 'dockerhub-credentials', variable: 'DOCKER_TOKEN')]) {
                    bat 'docker login -u omarnoman -p %DOCKER_TOKEN%'
                }   

                // Push tags
                bat "docker push omarnoman/python_login_webapp:${BUILDTAG}"
                bat "docker push omarnoman/python_login_webapp:latest"

                echo "Image pushed to Docker Hub"

                // Run a new production container
                bat """
                docker stop python_login_webapp-prod || echo "No running production container"
                docker rm python_login_webapp-prod || echo "No old container to remove"
                """
                
                bat """
                docker run -d --name python_login_webapp-prod -e ENV=production -p 80:5000 omarnoman/python_login_webapp:${BUILDTAG}
                """

                bat "docker ps -a"
            }
        }

        stage('Monitoring') {
            steps {
                echo 'Monitoring stage'
                bat 'docker stop dd-agent || echo No existing Datadog container running'
                bat 'docker rm -f dd-agent || echo No existing Datadog container to remove'
                

                withCredentials([string(credentialsId: 'datadog_api', variable: 'API_KEY')]) {
                    
                    bat '''
                    docker run -d --name dd-agent \
                        -e DD_API_KEY=%API_KEY% \
                        -e DD_SITE="ap2.datadoghq.com" \
                        -e DD_DOGSTATSD_NON_LOCAL_TRAFFIC=true \
                        -v /var/run/docker.sock:/var/run/docker.sock:ro \
                        -v /proc/:/host/proc/:ro \
                        -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
                        -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
                        gcr.io/datadoghq/agent:7
                    '''
                }
                echo "Datadog has started monitoring"

            }
        }
    }
}













