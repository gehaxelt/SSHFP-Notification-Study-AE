Almost all scripts and tools used in this research are either Python- or Bash-Script-based. Further, most of these tools or scripts are containerized with Docker [0] and Docker-Compose [1]. Sometimes, you might need to use a Python3 environment with some packages installed.
For the statistical analysis, we used IBM SPSS. Accordingly, we also provided the SPSS syntax. However, the calculations can be done with any other tool for statistical analysis.

We used our containers and scripts on x86_64/amd64-based hardware, so we cannot tell whether it runs on ARM-based or Apple Silicon-based (M*-CPUs) systems. Furthermore, the scripts may expect a linux-based system, i.e. Ubuntu/Debian/Archlinux, etc. and may not work on Windows, MacOs, or other operating systems.

However, there should not be any special hardware requirements that go above an average consumer laptop (8GB RAM, 4 Cores). 

[0] https://docs.docker.com/engine/install/
[1] https://github.com/docker/compose/