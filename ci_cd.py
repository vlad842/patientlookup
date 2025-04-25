"""
Patient Lookup CI/CD Deployment Script

This script provides a comprehensive set of commands for building, testing, and deploying
the Patient Lookup application using Docker, either locally or on AWS EC2.

Available Commands:
------------------
1. Build and Test:
   python ci_cd.py build      # Build the application
   python ci_cd.py test       # Run tests

2. Local Docker Operations:
   python ci_cd.py start      # Start the application locally
   python ci_cd.py start --force  # Force rebuild and start
   python ci_cd.py stop       # Stop the application
   python ci_cd.py restart    # Restart the application
   python ci_cd.py restart --force  # Force rebuild and restart

3. AWS EC2 Docker Operations:
   python ci_cd.py ec2-deploy     # Deploy Docker setup to EC2
   python ci_cd.py ec2-start      # Start Docker containers on EC2
   python ci_cd.py ec2-stop       # Stop Docker containers on EC2
   python ci_cd.py ec2-restart    # Restart Docker containers on EC2

4. Full Deployment:
   python ci_cd.py full           # Full local deployment
   python ci_cd.py full-ec2       # Full EC2 deployment

5. Maintenance:
   python ci_cd.py clean          # Clean up Docker resources

Environment Requirements:
- Docker (for both local and EC2)
- Docker Compose
- AWS CLI configured
- Maven
- Python 3.6+

The application will be available at http://localhost:8080 when running.
"""

import os
import subprocess
import shutil
import sys
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class Deployer:
    def __init__(self):
        self.APP_NAME = "patientlookup"
        self.TARGET_JAR = f"target/{self.APP_NAME}-0.0.1-SNAPSHOT.jar"
        self.DEPLOY_DIR = "deployed/"
        self.DOCKER_IMAGE = f"{self.APP_NAME}-api"
        self.EC2_HOST = os.getenv('EC2_HOST')  # e.g., ec2-user@1.2.3.4 or the full hostname
        self.EC2_USERNAME = os.getenv('EC2_USERNAME', 'ubuntu')
        self.EC2_APP_DIR = '/home/ubuntu/app'
        self.SSH_KEY_PATH = os.getenv('SSH_KEY_PATH', '~/.ssh/ec2-key.pem')

    def print_step(self, message: str, color: str = Colors.NC):
        print(f"{color}🔍 {message}{Colors.NC}")

    def run(self, command: str, label: Optional[str] = None) -> bool:
        if label:
            self.print_step(f"Running: {label}", Colors.YELLOW)
        print(f"Executing: {command}")
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            self.print_step(f"Step failed: {label or command}", Colors.RED)
            return False
        return True

    def check_requirements(self) -> bool:
        self.print_step("Checking requirements...", Colors.YELLOW)
        required_commands = ['docker', 'docker-compose', 'mvn', 'aws']
        missing = []
        
        for cmd in required_commands:
            if not shutil.which(cmd):
                missing.append(cmd)
        
        if missing:
            self.print_step(f"Missing required tools: {', '.join(missing)}", Colors.RED)
            return False
        
        self.print_step("All requirements met!", Colors.GREEN)
        return True

    def build(self) -> bool:
        if not self.run("mvn clean package -DskipTests", "Build with Maven"):
            return False
        return True

    def test(self) -> bool:
        if not self.run("mvn test", "Run Tests"):
            return False
        return True

    def install_docker_on_ec2(self) -> bool:
        if not self.EC2_HOST:
            self.print_step("ERROR: EC2_HOST not set in .env file!", Colors.RED)
            return False

        # Install Docker
        ssh_command = f'ssh -i "{self.SSH_KEY_PATH}" {self.EC2_HOST} "sudo apt update && sudo apt install -y docker.io"'
        if not self.run(ssh_command, "Install Docker"):
            return False

        # Install Docker Compose
        ssh_command = f'ssh -i "{self.SSH_KEY_PATH}" {self.EC2_HOST} "sudo apt install -y docker-compose"'
        if not self.run(ssh_command, "Install Docker Compose"):
            return False

        # Add user to docker group
        ssh_command = f'ssh -i "{self.SSH_KEY_PATH}" {self.EC2_HOST} "sudo usermod -aG docker ubuntu"'
        if not self.run(ssh_command, "Add user to docker group"):
            return False

        self.print_step("Docker and Docker Compose installed successfully!", Colors.GREEN)
        return True

    def deploy_to_ec2(self) -> bool:
        if not os.path.exists(self.TARGET_JAR):
            self.print_step("ERROR: Build JAR not found!", Colors.RED)
            return False

        if not self.EC2_HOST:
            self.print_step("ERROR: EC2_HOST not set in .env file!", Colors.RED)
            return False

        # Install Docker and Docker Compose if needed
        if not self.install_docker_on_ec2():
            return False

        # Check if directory exists and create if it doesn't
        ssh_command = f'ssh -i "{self.SSH_KEY_PATH}" {self.EC2_HOST} "if [ ! -d {self.EC2_APP_DIR} ]; then mkdir -p {self.EC2_APP_DIR}; fi"'
        if not self.run(ssh_command, "Check/Create app directory on EC2"):
            return False

        # Create .env file on EC2
        env_content = f"DB_PASSWORD={os.getenv('DB_PASSWORD')}"
        ssh_command = f'ssh -i "{self.SSH_KEY_PATH}" {self.EC2_HOST} "echo \\"{env_content}\\" > {self.EC2_APP_DIR}/.env"'
        if not self.run(ssh_command, "Create .env file on EC2"):
            return False

        # Copy Docker Compose file
        scp_command = f'scp -i "{self.SSH_KEY_PATH}" docker-compose.yml {self.EC2_HOST}:{self.EC2_APP_DIR}/'
        if not self.run(scp_command, "Copy Docker Compose file to EC2"):
            return False

        # Copy Dockerfile
        scp_command = f'scp -i "{self.SSH_KEY_PATH}" Dockerfile {self.EC2_HOST}:{self.EC2_APP_DIR}/'
        if not self.run(scp_command, "Copy Dockerfile to EC2"):
            return False

        # Copy pom.xml
        scp_command = f'scp -i "{self.SSH_KEY_PATH}" pom.xml {self.EC2_HOST}:{self.EC2_APP_DIR}/'
        if not self.run(scp_command, "Copy pom.xml to EC2"):
            return False

        # Create src directory on EC2
        ssh_command = f'ssh -i "{self.SSH_KEY_PATH}" {self.EC2_HOST} "mkdir -p {self.EC2_APP_DIR}/src"'
        if not self.run(ssh_command, "Create src directory on EC2"):
            return False

        # Copy src directory recursively
        scp_command = f'scp -i "{self.SSH_KEY_PATH}" -r src/* {self.EC2_HOST}:{self.EC2_APP_DIR}/src/'
        if not self.run(scp_command, "Copy src directory to EC2"):
            return False

        # Copy JAR to EC2
        scp_command = f'scp -i "{self.SSH_KEY_PATH}" {self.TARGET_JAR} {self.EC2_HOST}:{self.EC2_APP_DIR}/'
        if not self.run(scp_command, "Copy JAR to EC2"):
            return False

        # Copy production properties
        scp_command = f'scp -i "{self.SSH_KEY_PATH}" src/main/resources/application-prod.properties {self.EC2_HOST}:{self.EC2_APP_DIR}/'
        if not self.run(scp_command, "Copy properties to EC2"):
            return False

        self.print_step("Deployed to EC2 successfully!", Colors.GREEN)
        return True

    def start_on_ec2(self) -> bool:
        if not self.EC2_HOST:
            self.print_step("ERROR: EC2_HOST not set in .env file!", Colors.RED)
            return False

        # SSH command to start Docker containers
        ssh_command = f"ssh -i {self.SSH_KEY_PATH} {self.EC2_HOST} 'cd {self.EC2_APP_DIR} && " \
                     f"export DB_PASSWORD={os.getenv('DB_PASSWORD')} && " \
                     f"docker-compose up -d'"
        
        if not self.run(ssh_command, "Start Docker containers on EC2"):
            return False

        self.print_step(f"Application started on EC2", Colors.GREEN)
        return True

    def stop_on_ec2(self) -> bool:
        if not self.EC2_HOST:
            self.print_step("ERROR: EC2_HOST not set in .env file!", Colors.RED)
            return False

        # SSH command to stop Docker containers
        ssh_command = f"ssh -i {self.SSH_KEY_PATH} {self.EC2_HOST} 'cd {self.EC2_APP_DIR} && docker-compose down'"
        
        if not self.run(ssh_command, "Stop Docker containers on EC2"):
            return False

        self.print_step("Application stopped on EC2", Colors.GREEN)
        return True

    def restart_on_ec2(self) -> bool:
        if not self.stop_on_ec2():
            return False
        return self.start_on_ec2()

    def full_ec2_deploy(self) -> bool:
        if not self.check_requirements():
            return False
        if not self.build():
            return False
        if not self.test():
            return False
        if not self.deploy_to_ec2():
            return False
        if not self.start_on_ec2():
            return False
        return True

    def docker_build(self) -> bool:
        if not self.run("docker-compose build", "Docker Compose Build"):
            return False
        return True

    def docker_start(self, force_rebuild: bool = False) -> bool:
        # Check if we need to build
        if force_rebuild or not os.path.exists(self.TARGET_JAR):
            self.print_step("Building application...", Colors.YELLOW)
            if not self.build():
                return False
            if not self.docker_build():
                return False

        if not self.run("docker-compose up -d", "Start Docker Compose"):
            return False
        self.print_step("Application is running at http://localhost:8080", Colors.GREEN)
        return True

    def docker_stop(self) -> bool:
        if not self.run("docker-compose down", "Stop Docker Compose"):
            return False
        return True

    def docker_restart(self, force_rebuild: bool = False) -> bool:
        if not self.docker_stop():
            return False
        return self.docker_start(force_rebuild)

    def cleanup(self) -> bool:
        self.print_step("Cleaning up...", Colors.YELLOW)
        if not self.run("docker system prune -f", "Clean Docker"):
            return False
        return True

    def full_deploy(self) -> bool:
        if not self.check_requirements():
            return False
        if not self.build():
            return False
        if not self.test():
            return False
        if not self.docker_build():
            return False
        if not self.docker_start():
            return False
        return True

    def check_ec2_status(self) -> bool:
        if not self.EC2_HOST:
            self.print_step("ERROR: EC2_HOST not set in .env file!", Colors.RED)
            return False

        # Check Docker containers status
        ssh_command = f'ssh -i "{self.SSH_KEY_PATH}" {self.EC2_HOST} "cd {self.EC2_APP_DIR} && docker-compose ps"'
        if not self.run(ssh_command, "Check Docker containers status"):
            return False

        # Check application logs
        ssh_command = f'ssh -i "{self.SSH_KEY_PATH}" {self.EC2_HOST} "cd {self.EC2_APP_DIR} && docker-compose logs --tail=50"'
        if not self.run(ssh_command, "View application logs"):
            return False

        return True

    def view_ec2_logs(self) -> bool:
        if not self.EC2_HOST:
            self.print_step("ERROR: EC2_HOST not set in .env file!", Colors.RED)
            return False

        # View application logs with follow option
        ssh_command = f'ssh -i "{self.SSH_KEY_PATH}" {self.EC2_HOST} "cd {self.EC2_APP_DIR} && docker-compose logs -f"'
        if not self.run(ssh_command, "View application logs (live)"):
            return False

        return True

def print_usage():
    print("Usage: python ci_cd.py [command] [options]")
    print("\nCommands:")
    print("  build         - Build the application")
    print("  test          - Run tests")
    print("  start         - Start the application locally")
    print("  stop          - Stop the application locally")
    print("  restart       - Restart the application locally")
    print("  ec2-deploy    - Deploy Docker setup to EC2")
    print("  ec2-start     - Start Docker containers on EC2")
    print("  ec2-stop      - Stop Docker containers on EC2")
    print("  ec2-restart   - Restart Docker containers on EC2")
    print("  ec2-status    - Check status of EC2 deployment")
    print("  ec2-logs      - View EC2 application logs")
    print("  ec2-install-docker - Install Docker and Docker Compose on EC2")
    print("  full          - Full local deployment")
    print("  full-ec2      - Full EC2 deployment")
    print("  clean         - Clean up Docker resources")
    print("\nOptions:")
    print("  --force       - Force rebuild when starting/restarting")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    deployer = Deployer()
    command = sys.argv[1]
    force_rebuild = "--force" in sys.argv

    if command == "build":
        deployer.build()
    elif command == "test":
        deployer.test()
    elif command == "start":
        deployer.docker_start(force_rebuild)
    elif command == "stop":
        deployer.docker_stop()
    elif command == "restart":
        deployer.docker_restart(force_rebuild)
    elif command == "ec2-deploy":
        deployer.deploy_to_ec2()
    elif command == "ec2-start":
        deployer.start_on_ec2()
    elif command == "ec2-stop":
        deployer.stop_on_ec2()
    elif command == "ec2-restart":
        deployer.restart_on_ec2()
    elif command == "ec2-status":
        deployer.check_ec2_status()
    elif command == "ec2-logs":
        deployer.view_ec2_logs()
    elif command == "ec2-install-docker":
        deployer.install_docker_on_ec2()
    elif command == "full":
        deployer.full_deploy()
    elif command == "full-ec2":
        deployer.full_ec2_deploy()
    elif command == "clean":
        deployer.cleanup()
    else:
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()