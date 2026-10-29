# S3(E3 部署與網路):單一 image,同一個 port 送前端建置產物與 WebSocket(research R11)
# build context 是 repo 根目錄(compose.yaml 的 build.context: ..)

FROM node:22-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
COPY shared/package.json shared/
COPY backend/package.json backend/
COPY frontend/package.json frontend/
COPY e2e/package.json e2e/
RUN npm ci
COPY shared/ shared/
COPY frontend/ frontend/
RUN npm run build --workspace frontend

FROM node:22-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
COPY shared/package.json shared/
COPY backend/package.json backend/
COPY frontend/package.json frontend/
COPY e2e/package.json e2e/
RUN npm ci --omit=dev --workspace backend --include-workspace-root

FROM node:22-slim
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY package.json ./
COPY shared/package.json shared/
COPY shared/src/ shared/src/
COPY backend/package.json backend/
COPY backend/src/ backend/src/
COPY --from=build /app/frontend/dist ./frontend/dist
USER node
EXPOSE 8080
# Node 22 原生 type stripping 直接執行 .ts,不設編譯步驟(research R2)
CMD ["node", "backend/src/server.ts"]
