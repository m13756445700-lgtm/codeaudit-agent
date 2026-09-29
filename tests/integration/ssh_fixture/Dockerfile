FROM codeaudit-runtime-base:2.0
USER root
RUN sed -i 's|http://mirrors.tuna.tsinghua.edu.cn/debian|https://deb.debian.org/debian|g' /etc/apt/sources.list.d/debian.sources && apt-get update && apt-get install -y --no-install-recommends openssh-server && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /run/sshd && git config --system --add safe.directory /fixture/repo.git
ENTRYPOINT ["/usr/sbin/sshd", "-D", "-e", "-p", "2222", "-o", "PasswordAuthentication=no", "-o", "PermitRootLogin=prohibit-password", "-o", "AuthorizedKeysFile=/fixture/id.pub", "-o", "StrictModes=no"]
