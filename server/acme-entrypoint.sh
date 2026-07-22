#!/usr/bin/env bash
set -Eeuo pipefail

readonly CHECK_INTERVAL="${ACME_CHECK_INTERVAL:-43200}"
readonly CERT_NAME="${ACME_CERT_NAME:-georeport.ru}"
readonly DOMAINS="${ACME_DOMAINS:-georeport.ru}"
readonly WEBROOT="/var/www/certbot"
readonly CERT_DIR="/certs"
readonly LIVE_DIR="/etc/letsencrypt/live/${CERT_NAME}"

NGINX_PID=""

log() {
    printf '%s [acme] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*"
}

validate_configuration() {
    if [[ -z "${ACME_EMAIL:-}" ]]; then
        log "ERROR: ACME_EMAIL is required"
        exit 1
    fi

    if ! [[ "${CHECK_INTERVAL}" =~ ^[0-9]+$ ]] || (( CHECK_INTERVAL < 60 )); then
        log "ERROR: ACME_CHECK_INTERVAL must be an integer of at least 60 seconds"
        exit 1
    fi

    mkdir -p "${CERT_DIR}" "${WEBROOT}"
}

certbot_arguments() {
    CERTBOT_ARGS=(
        --non-interactive
        --agree-tos
        --email "${ACME_EMAIL}"
        --cert-name "${CERT_NAME}"
        --keep-until-expiring
    )

    IFS=',' read -ra domain_list <<< "${DOMAINS}"
    for domain in "${domain_list[@]}"; do
        domain="${domain//[[:space:]]/}"
        if [[ -n "${domain}" ]]; then
            CERTBOT_ARGS+=(-d "${domain}")
        fi
    done

    if [[ "${ACME_STAGING:-false}" == "true" ]]; then
        CERTBOT_ARGS+=(--staging)
    fi
}

deploy_certificate() {
    if [[ ! -s "${LIVE_DIR}/fullchain.pem" || ! -s "${LIVE_DIR}/privkey.pem" ]]; then
        log "ERROR: Certbot did not create a complete certificate"
        return 1
    fi

    install -m 0644 "${LIVE_DIR}/fullchain.pem" "${CERT_DIR}/.crt.crt.new"
    install -m 0600 "${LIVE_DIR}/privkey.pem" "${CERT_DIR}/.key.key.new"
    mv -f "${CERT_DIR}/.crt.crt.new" "${CERT_DIR}/crt.crt"
    mv -f "${CERT_DIR}/.key.key.new" "${CERT_DIR}/key.key"
    log "Certificate deployed to ${CERT_DIR}/crt.crt and ${CERT_DIR}/key.key"
}

external_certificate_is_current() {
    [[ -s "${CERT_DIR}/crt.crt" && -s "${CERT_DIR}/key.key" ]] \
        && openssl x509 -in "${CERT_DIR}/crt.crt" -noout -checkend 0 >/dev/null 2>&1
}

issue_standalone() {
    log "Requesting certificate with emergency standalone validation"
    certbot certonly "${CERTBOT_ARGS[@]}" \
        --standalone \
        --preferred-challenges http
    deploy_certificate
}

start_nginx() {
    log "Starting NGINX"
    nginx -g 'daemon off;' &
    NGINX_PID=$!
    sleep 1

    if ! kill -0 "${NGINX_PID}" 2>/dev/null; then
        wait "${NGINX_PID}" || true
        NGINX_PID=""
        return 1
    fi
}

stop_nginx() {
    if [[ -z "${NGINX_PID}" ]] || ! kill -0 "${NGINX_PID}" 2>/dev/null; then
        return
    fi

    log "Stopping NGINX for standalone validation"
    nginx -s quit || kill -TERM "${NGINX_PID}"

    for _ in $(seq 1 30); do
        if ! kill -0 "${NGINX_PID}" 2>/dev/null; then
            wait "${NGINX_PID}" || true
            NGINX_PID=""
            return
        fi
        sleep 1
    done

    kill -TERM "${NGINX_PID}" 2>/dev/null || true
    wait "${NGINX_PID}" || true
    NGINX_PID=""
}

reload_nginx() {
    if nginx -t; then
        nginx -s reload
        log "NGINX reloaded with the current certificate"
    else
        log "ERROR: NGINX configuration test failed after certificate deployment"
        return 1
    fi
}

renew_certificate() {
    local old_fingerprint=""
    local new_fingerprint=""

    if [[ -s "${CERT_DIR}/crt.crt" ]]; then
        old_fingerprint="$(openssl x509 -in "${CERT_DIR}/crt.crt" -noout -fingerprint -sha256 2>/dev/null || true)"
    fi

    log "Checking certificate with webroot validation"
    if certbot certonly "${CERTBOT_ARGS[@]}" \
        --webroot \
        --webroot-path "${WEBROOT}" \
        --preferred-challenges http; then
        deploy_certificate
        new_fingerprint="$(openssl x509 -in "${CERT_DIR}/crt.crt" -noout -fingerprint -sha256)"
        if [[ "${new_fingerprint}" != "${old_fingerprint}" ]]; then
            reload_nginx
        else
            log "Certificate is not due for renewal"
        fi
        return
    fi

    log "Webroot validation failed; activating standalone fallback"
    stop_nginx
    if issue_standalone; then
        start_nginx
    else
        log "ERROR: Standalone validation also failed; restoring NGINX"
        start_nginx
        return 1
    fi
}

shutdown() {
    log "Shutting down"
    stop_nginx
    exit 0
}

validate_configuration
certbot_arguments
trap shutdown TERM INT

if [[ -s "${LIVE_DIR}/fullchain.pem" && -s "${LIVE_DIR}/privkey.pem" ]]; then
    deploy_certificate
elif ! external_certificate_is_current; then
    issue_standalone
fi

if ! start_nginx; then
    log "NGINX could not start with the external certificate; requesting a replacement"
    issue_standalone
    start_nginx
fi

while kill -0 "${NGINX_PID}" 2>/dev/null; do
    renew_certificate || true

    remaining="${CHECK_INTERVAL}"
    while (( remaining > 0 )); do
        step=30
        if (( remaining < step )); then
            step="${remaining}"
        fi
        sleep "${step}" &
        wait $! || true
        kill -0 "${NGINX_PID}" 2>/dev/null || break 2
        remaining=$((remaining - step))
    done
done

log "ERROR: NGINX exited unexpectedly"
wait "${NGINX_PID}" || true
exit 1
