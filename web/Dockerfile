FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Empty = same-origin /api via server.mjs (needed on Render *.onrender.com).
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build
ENV PORT=10000
ENV API_UPSTREAM=http://127.0.0.1:8000
EXPOSE 10000
CMD ["node", "server.mjs"]











