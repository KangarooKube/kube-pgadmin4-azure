# Build pgAdmin4 on UBI10 and includes PostgreSQL client binaries
# Usage:
#  build --build-arg PGADMIN_VERSION=9.8 -t kube-pgadmin4-azure:ubi10 .

ARG PGADMIN_VERSION=9

FROM dpage/pgadmin4:${PGADMIN_VERSION} AS dpage-pgadmin4

FROM registry.access.redhat.com/ubi10/ubi:latest AS builder-ubi10
ARG TARGETARCH
ARG TARGETVARIANT

RUN --mount=type=secret,id=rhsm_user \
    --mount=type=secret,id=rhsm_pass \
    export RHSM_USER=$(cat /run/secrets/rhsm_user) && \
    export RHSM_PASS=$(cat /run/secrets/rhsm_pass) && \
    subscription-manager register --username=${RHSM_USER} --password=${RHSM_PASS} && \
    # Map build TARGETARCH -> repo arch string (amd64 -> x86_64, arm64 -> aarch64)
    case "${TARGETARCH}${TARGETVARIANT:+-${TARGETVARIANT}}" in \
      amd64*) CR_ARCH="x86_64" ;; \
      x86_64*) CR_ARCH="x86_64" ;; \
      arm64*) CR_ARCH="aarch64" ;; \
      aarch64*) CR_ARCH="aarch64" ;; \
      ppc64le*) CR_ARCH="ppc64le" ;; \
      s390x*) CR_ARCH="s390x" ;; \
      *) CR_ARCH="${TARGETARCH}" ;; \
    esac && \
    echo "Enabling CodeReady repo for arch=${CR_ARCH} (TARGETARCH=${TARGETARCH} TARGETVARIANT=${TARGETVARIANT})" && \
    subscription-manager repos --enable=codeready-builder-for-rhel-10-${CR_ARCH}-rpms
RUN dnf -y install --assumeyes --nogpgcheck \
    https://download.postgresql.org/pub/repos/yum/reporpms/EL-10-${CR_ARCH}/pgdg-redhat-repo-latest.noarch.rpm && \
    dnf -y update && \
    dnf -y install --assumeyes \
      postgresql13 postgresql13-contrib \
      postgresql14 postgresql14-contrib \
      postgresql15 postgresql15-contrib \
      postgresql16 postgresql16-contrib \
      postgresql17 postgresql17-contrib \
      postgresql17-devel && \
    dnf -y install --assumeyes --allowerasing \
      python3 python3-pip python3-devel \
      libffi-devel openssl-devel \
      ca-certificates which wget unzip \
      sqlite sqlite-devel curl \
      procps shadow-utils sudo bash krb5-devel && \
    dnf clean all && \
    dnf makecache && \
    ln -s /usr/pgsql-17/bin/pg_config /usr/bin/pg_config

RUN curl https://raw.githubusercontent.com/pgadmin-org/pgadmin4/refs/heads/master/requirements.txt -o /tmp/requirements.txt && \
    python3 -m venv --system-site-packages --without-pip /venv && \
    /venv/bin/python3 -m pip install --no-cache-dir -r /tmp/requirements.txt && \
    /venv/bin/python3 -m pip install --no-cache-dir gunicorn && \
    rm -f /tmp/requirements.txt

# Use specific Postgres client versions as needed
# env & app builder steps are intentionally simple here since we will pip-install pgadmin in final image
# Final runtime image based on UBI10
FROM registry.access.redhat.com/ubi10/ubi:latest AS pgadmin-ubi10
ARG PGADMIN_VERSION

USER root

# Install runtime deps consistent with dpage image: python, libs, tools, sqlite, sudo, etc.
RUN dnf -y update && \
    dnf -y upgrade && \
    dnf -y install --assumeyes --allowerasing \
      python3 python3-pip python3-devel \
      libffi-devel openssl-devel \
      ca-certificates which wget unzip \
      sqlite sqlite-devel curl \
      procps shadow-utils sudo bash krb5-libs && \
    dnf clean all && \
    dnf makecache

# Copy the PG binaries we need from the postgres-ubi10 stage (from correct paths)
COPY --from=builder-ubi10 /usr/pgsql-13/bin/pg_dump /usr/local/pgsql-13/
COPY --from=builder-ubi10 /usr/pgsql-13/bin/pg_dumpall /usr/local/pgsql-13/
COPY --from=builder-ubi10 /usr/pgsql-13/bin/pg_restore /usr/local/pgsql-13/
COPY --from=builder-ubi10 /usr/pgsql-13/bin/psql /usr/local/pgsql-13/

COPY --from=builder-ubi10 /usr/pgsql-14/bin/pg_dump /usr/local/pgsql-14/
COPY --from=builder-ubi10 /usr/pgsql-14/bin/pg_dumpall /usr/local/pgsql-14/
COPY --from=builder-ubi10 /usr/pgsql-14/bin/pg_restore /usr/local/pgsql-14/
COPY --from=builder-ubi10 /usr/pgsql-14/bin/psql /usr/local/pgsql-14/

COPY --from=builder-ubi10 /usr/pgsql-15/bin/pg_dump /usr/local/pgsql-15/
COPY --from=builder-ubi10 /usr/pgsql-15/bin/pg_dumpall /usr/local/pgsql-15/
COPY --from=builder-ubi10 /usr/pgsql-15/bin/pg_restore /usr/local/pgsql-15/
COPY --from=builder-ubi10 /usr/pgsql-15/bin/psql /usr/local/pgsql-15/

COPY --from=builder-ubi10 /usr/pgsql-16/bin/pg_dump /usr/local/pgsql-16/
COPY --from=builder-ubi10 /usr/pgsql-16/bin/pg_dumpall /usr/local/pgsql-16/
COPY --from=builder-ubi10 /usr/pgsql-16/bin/pg_restore /usr/local/pgsql-16/
COPY --from=builder-ubi10 /usr/pgsql-16/bin/psql /usr/local/pgsql-16/

COPY --from=builder-ubi10 /usr/pgsql-17/bin/pg_dump /usr/local/pgsql-17/
COPY --from=builder-ubi10 /usr/pgsql-17/bin/pg_dumpall /usr/local/pgsql-17/
COPY --from=builder-ubi10 /usr/pgsql-17/bin/pg_restore /usr/local/pgsql-17/
COPY --from=builder-ubi10 /usr/pgsql-17/bin/psql /usr/local/pgsql-17/

COPY --from=builder-ubi10 /usr/pgsql-17/lib/libpq.so.5 /usr/lib64/
COPY --from=builder-ubi10 /venv /venv

COPY --from=dpage-pgadmin4 /pgadmin4 /pgadmin4
COPY --from=dpage-pgadmin4 /entrypoint.sh /entrypoint.sh

RUN if [ -x "/usr/local/pgsql-17/psql" ]; then \
      ln -sf "/usr/local/pgsql-17/psql" /usr/bin/psql; \
      ln -sf "/usr/local/pgsql-17/pg_dump" /usr/bin/pg_dump; \
      ln -sf "/usr/local/pgsql-17/pg_dumpall" /usr/bin/pg_dumpall; \
      ln -sf "/usr/local/pgsql-17/pg_restore" /usr/bin/pg_restore; \
      ln -sf "/usr/local/pgsql-17/pg_config" /usr/bin/pg_config; \
    fi

# Create directories and user similar to upstream image
RUN useradd -u 5050 -m -d /var/lib/pgadmin -s /sbin/nologin pgadmin || true && \
    mkdir -p /var/lib/pgadmin /var/log/pgadmin /var/lib/pgadmin/sessions /var/lib/pgadmin/storage /usr/local/pgsql /pgadmin4 && \
    chown -R pgadmin:pgadmin /var/lib/pgadmin /var/log/pgadmin /var/lib/pgadmin/sessions /var/lib/pgadmin/storage /pgadmin4 && \
    chmod 700 /var/lib/pgadmin && \
    chmod 700 /var/lib/pgadmin/sessions && \
    chmod 700 /var/lib/pgadmin/storage && \
    chmod 700 /var/log/pgadmin

# Create per-version symlinks for psql and tools
RUN if [ -x "/usr/local/pgsql-17/psql" ]; then \
      ln -sf "/usr/local/pgsql-17/psql" /usr/bin/psql; \
      ln -sf "/usr/local/pgsql-17/pg_dump" /usr/bin/pg_dump; \
      ln -sf "/usr/local/pgsql-17/pg_dumpall" /usr/bin/pg_dumpall; \
      ln -sf "/usr/local/pgsql-17/pg_restore" /usr/bin/pg_restore; \
    fi

# Expose ports and set workdir
EXPOSE 80 443
WORKDIR /pgadmin4
ENV PYTHONPATH=/pgadmin4

# Set config options via env vars
ENV PGADMIN_CONFIG_SERVER_MODE=True

# switch to pgadmin user for runtime
USER pgadmin
ENV PATH=/venv/bin:$PATH

# default entry (pip package exposes module)
CMD ["/entrypoint.sh"]