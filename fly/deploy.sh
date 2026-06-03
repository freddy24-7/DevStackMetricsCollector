#!/bin/sh
# Deploy all services to Fly.io in dependency order.
# Prerequisites:
#   - flyctl installed and authenticated (fly auth login)
#   - All app names below match your fly.toml files
#   - Run once: fly postgres create --name metrics-db --region lhr

set -e

REGION="lhr"
ADMIN_APP="metrics-admin-freddy"
COLLECTOR_APP="metrics-collector-freddy"
GATEWAY_APP="metrics-gateway-freddy"
NGINX_APP="metrics-nginx-freddy"
DB_APP="metrics-db-freddy"

echo "==> Attaching database to services..."
fly postgres attach $DB_APP --app $ADMIN_APP    || true
fly postgres attach $DB_APP --app $COLLECTOR_APP || true
fly postgres attach $DB_APP --app $GATEWAY_APP   || true

echo "==> Setting secrets..."
# Replace these values with real production secrets
fly secrets set \
  DJANGO_SECRET_KEY="$(openssl rand -hex 32)" \
  DEBUG="false" \
  --app $ADMIN_APP

echo "==> Deploying admin (runs migrations)..."
fly deploy --config services/admin/fly.toml --dockerfile services/admin/Dockerfile

echo "==> Deploying collector..."
fly deploy --config services/collector/fly.toml --dockerfile services/collector/Dockerfile

echo "==> Deploying gateway..."
fly deploy --config services/gateway/fly.toml --dockerfile services/gateway/Dockerfile

echo "==> Deploying nginx..."
fly deploy --config nginx/fly.toml --dockerfile nginx/Dockerfile

echo ""
echo "Done. Your public URL is: https://$NGINX_APP.fly.dev"
