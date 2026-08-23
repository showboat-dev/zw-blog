FROM node:20-alpine

WORKDIR /app
COPY package.json .
RUN npm install --ignore-scripts || true
COPY . .
EXPOSE 4173
CMD ["npm", "run", "preview"]
