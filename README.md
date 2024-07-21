# MobSF Automation with Docker

This repository contains a script to automate the integration with Mobile Security Framework (MobSF) using Docker. The script allows you to upload an APK file to MobSF, trigger a scan, and fetch JSON and PDF reports.

## Prerequisites

Before running the script, ensure you have the following installed:

- Docker: Install Docker on your system. [Docker Installation Guide](https://docs.docker.com/get-docker/)
- Git: Install Git for version control. [Git Installation Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- Pull and Run MobSF
  ```bash
  docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/pentestguy/MobSF-Automation.git
   cd mob-sf-automation

2. Build the Docker image:
   ```bash
   docker build -t mobsf-automation

3. Run
   ```bash
   docker run --rm -v ${PWD}:/app mobsf-automation /app/your_app.apk --api-key YOUR_API_KEY --api-url YOUR_API_URL

## Use PreBuilt Docker Image

   ```bash
   docker run --rm -v ${PWD}:/app p3nt3stguy/mobsf-automation:latest /app/your_app.apk --api-key YOUR_API_KEY --api-url YOUR_API_URL
