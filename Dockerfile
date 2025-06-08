FROM google/cloud-sdk:emulators

# Install curl, nodejs, npm
RUN apt-get update && apt-get install -y curl \
  && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
  && apt-get install -y nodejs \
  && npm install -g firebase-tools \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Your existing commands
CMD ["gcloud", "config", "set", "project", "splitin-firebase"]
# (then start emulator, or override in docker-compose)