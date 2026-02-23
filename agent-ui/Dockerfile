FROM node:20-alpine
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile
COPY . .
ARG NEXT_PUBLIC_AGENTOS_URL=http://localhost:8000
ENV NEXT_PUBLIC_AGENTOS_URL=${NEXT_PUBLIC_AGENTOS_URL}
RUN pnpm build
ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000
CMD ["pnpm", "start"]
