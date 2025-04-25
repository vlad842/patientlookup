"""
Patient Lookup CI/CD Deployment Script

This script provides a comprehensive set of commands for building, testing, and deploying
the Patient Lookup application using Docker Compose.

Available Commands:
------------------
1. Build and Test:
   python ci_cd.py build      # Build the application
   python ci_cd.py test       # Run tests

2. Docker Operations:
   python ci_cd.py start      # Start the application (auto-builds if needed)
   python ci_cd.py start --force  # Force rebuild and start
   python ci_cd.py stop       # Stop the application
   python ci_cd.py restart    # Restart the application
   python ci_cd.py restart --force  # Force rebuild and restart

3. Deployment:
   python ci_cd.py deploy     # Deploy the JAR to deployment directory
   python ci_cd.py full       # Full deployment (build, test, deploy, start)

4. Maintenance:
   python ci_cd.py clean      # Clean up Docker resources

Environment Requirements:
- Docker
- Docker Compose
- Maven
- Python 3.6+

The application will be available at http://localhost:8080 when running.
"""

import os
import subprocess
import shutil
import sys
from typing import Optional

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
        required_commands = ['docker', 'docker-compose', 'mvn']
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

    def deploy(self) -> bool:
        if not os.path.exists(self.TARGET_JAR):
            self.print_step("ERROR: Build JAR not found!", Colors.RED)
            return False
        
        os.makedirs(self.DEPLOY_DIR, exist_ok=True)
        shutil.copy(self.TARGET_JAR, self.DEPLOY_DIR)
        self.print_step(f"Deployed to {self.DEPLOY_DIR}{os.path.basename(self.TARGET_JAR)}", Colors.GREEN)
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

def print_usage():
    print("Usage: python ci_cd.py [command] [options]")
    print("\nCommands:")
    print("  build     - Build the application")
    print("  test      - Run tests")
    print("  deploy    - Deploy the application")
    print("  start     - Start the application with Docker Compose")
    print("  stop      - Stop the application")
    print("  restart   - Restart the application")
    print("  clean     - Clean up Docker resources")
    print("  full      - Full deployment (build, test, deploy, start)")
    print("\nOptions:")
    print("  --force   - Force rebuild when starting/restarting")

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
    elif command == "deploy":
        deployer.deploy()
    elif command == "start":
        deployer.docker_start(force_rebuild)
    elif command == "stop":
        deployer.docker_stop()
    elif command == "restart":
        deployer.docker_restart(force_rebuild)
    elif command == "clean":
        deployer.cleanup()
    elif command == "full":
        deployer.full_deploy()
    else:
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()