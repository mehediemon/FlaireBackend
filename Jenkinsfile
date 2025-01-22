pipeline {
    agent any

    environment {
        EKS_CLUSTER_NAME = 'your-eks-cluster'
        AWS_REGION = 'your-region'
        DOCKER_HUB_USER = credentials('dockerhub-user')
        DOCKER_HUB_PASSWORD = credentials('dockerhub-password')
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build and Push Docker Images') {
            parallel {
                stage('Build Notification Service') {
                    steps {
                        dir('notification_service') {
                            script {
                                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                                    sh '''
                                    docker build -t mehedihub/notification-service:latest .
                                    docker push mehedihub/notification-service:latest
                                    '''
                                }
                            }
                        }
                    }
                }

                stage('Build Task Service') {
                    steps {
                        dir('task_service') {
                            script {
                                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                                    sh '''
                                    docker build -t mehedihub/task-service:latest .
                                    docker push mehedihub/task-service:latest
                                    '''
                                }
                            }
                        }
                    }
                }

                stage('Build User Service') {
                    steps {
                        dir('user_service') {
                            script {
                                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                                    sh '''
                                    docker build -t mehedihub/user-service:latest .
                                    docker push mehedihub/user-service:latest
                                    '''
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'), 
                                     string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')]) {
                        sh '''
                        aws eks --region ${AWS_REGION} update-kubeconfig --name ${EKS_CLUSTER_NAME}
                        kubectl apply -f notification_service/k8s/deployment.yml
                        kubectl apply -f notification_service/k8s/service.yml
                        kubectl apply -f task_service/k8s/deployment.yml
                        kubectl apply -f task_service/k8s/service.yml
                        kubectl apply -f user_service/k8s/deployment.yml
                        kubectl apply -f user_service/k8s/service.yml
                        '''
                    }
                }
            }
        }
    }
}
