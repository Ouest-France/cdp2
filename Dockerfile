FROM openpolicyagent/conftest:v0.55.0 AS conftest
FROM alpine:3.18

ARG VERSION_HADOLINT="v2.12.0"
ARG VERSION_KUBECTL="v1.29.0"
ARG VERSION_HELM="v3.13.0"
ARG VERSION_HELM2="v2.17.0"

COPY . cdp/
RUN mkdir -p /cdp/k8s/charts
COPY --from=conftest /conftest /bin/conftest

ADD https://github.com/hadolint/hadolint/releases/download/${VERSION_HADOLINT}/hadolint-Linux-x86_64 /bin/hadolint
ADD https://storage.googleapis.com/kubernetes-release/release/${VERSION_KUBECTL}/bin/linux/amd64/kubectl /bin/kubectl

WORKDIR /cdp

RUN apk -v --no-cache add tar ca-certificates python3  python3-dev  skopeo coreutils podman py3-setuptools py3-pip py3-wheel\
      groff less mailcap curl openrc build-base libgit2-dev autoconf automake libtool jq git openssh unzip \
    && chmod +x /bin/hadolint && chmod +x /bin/kubectl \
    && if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi \
    && if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
    && ln -s /usr/lib/libcurl.so.4 /usr/lib/libcurl-gnutls.so.4 \
    && pip install awscli --break-system-packages \
    && pip install --break-system-packages -r requirements.txt \
    && apk -v add gettext \
    && apk -v --no-cache --purge del py-pip autoconf automake libtool build-base libgit2-dev python3-dev \
    && curl -L https://get.helm.sh/helm-${VERSION_HELM}-linux-amd64.tar.gz | tar zxv -C /tmp/ --strip-components=1 linux-amd64/helm && mv /tmp/helm /bin/helm3 && chmod +x /bin/helm3 \
    && curl -L https://get.helm.sh/helm-${VERSION_HELM2}-linux-amd64.tar.gz | tar zxv -C /tmp/ --strip-components=1 linux-amd64/helm && mv /tmp/helm /bin/helm2 && chmod +x /bin/helm2 \
    && helm3 plugin install https://github.com/helm/helm-2to3 \
    && rm -rf /var/lib/apk/lists/* && rm -rf /var/cache/apk/* /root/.cache /usr/lib/python3.8/site-packages/pip /usr/lib/python3.8/__pycache__ /usr/lib/python3.8/site-packages/awscli/examples /usr/lib/python3.8/site-packages/config-3.8* \
    && mkdir -p /root/.docker 
RUN  python setup.py install && rm -rf /cdp/..?* .[!.]*


# Options Podman
ENV STORAGE_DRIVER=vfs
ENV STORAGE_OPTS=""

